import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.config import Config

from constants import (
    DEFAULT_ACCOUNT_ID,
    DEFAULT_REGION,
    LOCALSTACK_ENDPOINT,
    PRICING,
    REQUIRED_TAGS,
)


def utc_now():
    return datetime.now(timezone.utc)


def iso_timestamp():
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def get_ec2_client(region):
    return boto3.client(
        "ec2",
        region_name=region,
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 3, "mode": "standard"}),
    )


def tag_list_to_dict(tags):
    if not tags:
        return {}
    return {tag.get("Key"): tag.get("Value") for tag in tags}


def is_protected(tags):
    return str(tags.get("Protected", "")).lower() == "true"


def missing_required_tags(tags):
    return [key for key in REQUIRED_TAGS if not tags.get(key)]


def volume_monthly_cost(volume):
    size = volume.get("Size", 0)
    volume_type = volume.get("VolumeType", "gp3")

    if volume_type == "gp3":
        return round(size * PRICING["ebs_gp3_gb_month"], 2)

    return round(size * PRICING["ebs_gp3_gb_month"], 2)


def calculate_age_days(created_at):
    if not created_at:
        return 0

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return max((utc_now() - created_at).days, 0)


def build_finding(
    resource_id,
    resource_type,
    reason,
    age_days,
    estimated_monthly_cost_usd,
    tags,
    suggested_action,
    safe_to_auto_delete,
):
    return {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "reason": reason,
        "age_days": age_days,
        "estimated_monthly_cost_usd": estimated_monthly_cost_usd,
        "tags": tags,
        "suggested_action": suggested_action,
        "safe_to_auto_delete": safe_to_auto_delete,
    }


def find_unattached_ebs_volumes(ec2):
    findings = []

    response = ec2.describe_volumes(
        Filters=[
            {
                "Name": "status",
                "Values": ["available"],
            }
        ]
    )

    for volume in response.get("Volumes", []):
        tags = tag_list_to_dict(volume.get("Tags", []))
        age_days = calculate_age_days(volume.get("CreateTime"))

        findings.append(
            build_finding(
                resource_id=volume.get("VolumeId"),
                resource_type="ebs_volume",
                reason="unattached",
                age_days=age_days,
                estimated_monthly_cost_usd=volume_monthly_cost(volume),
                tags={key: tags.get(key) for key in REQUIRED_TAGS},
                suggested_action="delete",
                safe_to_auto_delete=False,
            )
        )

    return findings


def find_stopped_instances(ec2, stopped_days):
    findings = []

    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "instance-state-name",
                "Values": ["stopped"],
            }
        ]
    )

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            tags = tag_list_to_dict(instance.get("Tags", []))
            launch_time = instance.get("LaunchTime")
            age_days = calculate_age_days(launch_time)

            if age_days <= stopped_days:
                continue

            findings.append(
                build_finding(
                    resource_id=instance.get("InstanceId"),
                    resource_type="ec2_instance",
                    reason=f"stopped_more_than_{stopped_days}_days",
                    age_days=age_days,
                    estimated_monthly_cost_usd=PRICING["stopped_t3_micro_month"],
                    tags={key: tags.get(key) for key in REQUIRED_TAGS},
                    suggested_action="terminate",
                    safe_to_auto_delete=False,
                )
            )

    return findings


def find_unused_elastic_ips(ec2):
    findings = []

    response = ec2.describe_addresses()

    for address in response.get("Addresses", []):
        if address.get("InstanceId") or address.get("NetworkInterfaceId"):
            continue

        tags = tag_list_to_dict(address.get("Tags", []))
        resource_id = address.get("AllocationId") or address.get("PublicIp")

        findings.append(
            build_finding(
                resource_id=resource_id,
                resource_type="elastic_ip",
                reason="unused",
                age_days=0,
                estimated_monthly_cost_usd=PRICING["elastic_ip_month"],
                tags={key: tags.get(key) for key in REQUIRED_TAGS},
                suggested_action="release",
                safe_to_auto_delete=False,
            )
        )

    return findings


def find_missing_tags(ec2):
    findings = []

    findings.extend(find_missing_tags_on_instances(ec2))
    findings.extend(find_missing_tags_on_volumes(ec2))
    findings.extend(find_missing_tags_on_elastic_ips(ec2))

    return findings


def find_missing_tags_on_instances(ec2):
    findings = []

    response = ec2.describe_instances()

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            tags = tag_list_to_dict(instance.get("Tags", []))
            missing = missing_required_tags(tags)

            if not missing:
                continue

            findings.append(
                build_finding(
                    resource_id=instance.get("InstanceId"),
                    resource_type="ec2_instance",
                    reason=f"missing_tags:{','.join(missing)}",
                    age_days=calculate_age_days(instance.get("LaunchTime")),
                    estimated_monthly_cost_usd=0.00,
                    tags={key: tags.get(key) for key in REQUIRED_TAGS},
                    suggested_action="add_required_tags",
                    safe_to_auto_delete=False,
                )
            )

    return findings


def find_missing_tags_on_volumes(ec2):
    findings = []

    response = ec2.describe_volumes()

    for volume in response.get("Volumes", []):
        tags = tag_list_to_dict(volume.get("Tags", []))
        missing = missing_required_tags(tags)

        if not missing:
            continue

        findings.append(
            build_finding(
                resource_id=volume.get("VolumeId"),
                resource_type="ebs_volume",
                reason=f"missing_tags:{','.join(missing)}",
                age_days=calculate_age_days(volume.get("CreateTime")),
                estimated_monthly_cost_usd=0.00,
                tags={key: tags.get(key) for key in REQUIRED_TAGS},
                suggested_action="add_required_tags",
                safe_to_auto_delete=False,
            )
        )

    return findings


def find_missing_tags_on_elastic_ips(ec2):
    findings = []

    response = ec2.describe_addresses()

    for address in response.get("Addresses", []):
        tags = tag_list_to_dict(address.get("Tags", []))
        missing = missing_required_tags(tags)

        if not missing:
            continue

        resource_id = address.get("AllocationId") or address.get("PublicIp")

        findings.append(
            build_finding(
                resource_id=resource_id,
                resource_type="elastic_ip",
                reason=f"missing_tags:{','.join(missing)}",
                age_days=0,
                estimated_monthly_cost_usd=0.00,
                tags={key: tags.get(key) for key in REQUIRED_TAGS},
                suggested_action="add_required_tags",
                safe_to_auto_delete=False,
            )
        )

    return findings


def delete_findings(ec2, findings):
    deleted = []
    skipped = []

    for finding in findings:
        tags = finding.get("tags", {})

        if is_protected(tags):
            skipped.append(
                {
                    "resource_id": finding["resource_id"],
                    "reason": "Protected=true",
                }
            )
            continue

        resource_type = finding["resource_type"]
        action = finding["suggested_action"]
        resource_id = finding["resource_id"]

        try:
            if resource_type == "ebs_volume" and action == "delete":
                ec2.delete_volume(VolumeId=resource_id)
                deleted.append(resource_id)

            elif resource_type == "elastic_ip" and action == "release":
                ec2.release_address(AllocationId=resource_id)
                deleted.append(resource_id)

            elif resource_type == "ec2_instance" and action == "terminate":
                ec2.terminate_instances(InstanceIds=[resource_id])
                deleted.append(resource_id)

        except Exception as exc:
            skipped.append(
                {
                    "resource_id": resource_id,
                    "reason": str(exc),
                }
            )

    return deleted, skipped


def write_json_report(report, output_path):
    Path(output_path).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")


def write_markdown_report(report, output_path):
    lines = []

    lines.append("# Cost Janitor Report")
    lines.append("")
    lines.append(f"Scan timestamp: `{report['scan_timestamp']}`")
    lines.append(f"Region: `{report['region']}`")
    lines.append(f"Total findings: `{report['summary']['total_orphans']}`")
    lines.append(
        f"Estimated monthly waste: `${report['summary']['estimated_monthly_waste_usd']}`"
    )
    lines.append("")

    if not report["findings"]:
        lines.append("No orphaned or non-compliant resources were found.")
    else:
        lines.append("| Resource ID | Type | Reason | Age Days | Cost | Suggested Action |")
        lines.append("|---|---|---|---:|---:|---|")

        for finding in report["findings"]:
            lines.append(
                f"| {finding['resource_id']} "
                f"| {finding['resource_type']} "
                f"| {finding['reason']} "
                f"| {finding['age_days']} "
                f"| ${finding['estimated_monthly_cost_usd']} "
                f"| {finding['suggested_action']} |"
            )

    lines.append("")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def build_report(region, findings):
    total_cost = round(
        sum(item.get("estimated_monthly_cost_usd", 0.0) for item in findings), 2
    )

    return {
        "scan_timestamp": iso_timestamp(),
        "account_id": DEFAULT_ACCOUNT_ID,
        "region": region,
        "summary": {
            "total_orphans": len(findings),
            "estimated_monthly_waste_usd": total_cost,
        },
        "findings": findings,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="NimbusKart Cost Janitor")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Scan and report only. This is the default mode.",
    )
    mode.add_argument(
        "--delete",
        action="store_true",
        help="Delete eligible resources. Protected=true resources are always skipped.",
    )

    parser.add_argument(
        "--stopped-days",
        type=int,
        default=14,
        help="Flag stopped instances older than this many days.",
    )
    parser.add_argument(
        "--region",
        default=DEFAULT_REGION,
        help="AWS region to scan.",
    )
    parser.add_argument(
        "--json-output",
        default="report.json",
        help="Path for JSON report.",
    )
    parser.add_argument(
        "--md-output",
        default="report.md",
        help="Path for Markdown report.",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    ec2 = get_ec2_client(args.region)

    findings = []
    findings.extend(find_unattached_ebs_volumes(ec2))
    findings.extend(find_stopped_instances(ec2, args.stopped_days))
    findings.extend(find_unused_elastic_ips(ec2))
    findings.extend(find_missing_tags(ec2))

    deleted = []
    skipped = []

    if args.delete:
        deleted, skipped = delete_findings(ec2, findings)

    report = build_report(args.region, findings)

    if args.delete:
        report["delete_summary"] = {
            "deleted": deleted,
            "skipped": skipped,
        }

    write_json_report(report, args.json_output)
    write_markdown_report(report, args.md_output)

    print(f"JSON report written to {args.json_output}")
    print(f"Markdown report written to {args.md_output}")
    print(f"Findings: {report['summary']['total_orphans']}")

    if not args.delete and report["summary"]["total_orphans"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())