# Design Note

## Architecture

The Janitor is structured to separate core logic from cloud-specific code, so adding a new provider does not require touching the report or safety logic.

```
janitor/
  core/
    scanner.py
    finding.py
    report.py
    policy.py
  providers/
    aws/
      ec2.py
      ebs.py
      eip.py
      tags.py
```

The core layer understands resources, tags, findings, and safety rules. Each provider translates cloud-specific API responses into that common format.

---

## Permissions

**Dry-run mode** requires read-only access only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "ec2:DescribeTags"
      ],
      "Resource": "*"
    }
  ]
}
```

**Delete mode** requires a separate role with limited destructive actions (`ec2:DeleteVolume`, `ec2:ReleaseAddress`). It is not granted by default and should require explicit approval.

---

## Safety Rules

Before any resource is flagged for deletion, it must pass three checks:

- Minimum age threshold met (avoids resources mid-migration or mid-recovery)
- Not tagged `Protected=true`
- Not present in an allowlist

The script recommends deletion first. It does not delete automatically.

---

## Observability

| Metric | Alert Condition |
|---|---|
| `janitor_findings_total` | Findings increase across 3 consecutive runs |
| `estimated_monthly_waste_usd` | Exceeds $100 |
| `janitor_scan_success` | Scan fails |
| `untagged_resources_total` | Any production resource missing required tags |

---

## Current Status

Version 1 covers the Terraform baseline only. The Janitor script, GitHub Actions workflow, and multi-cloud provider modules are not yet implemented.
