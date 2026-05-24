# Design Note

## Architecture

Core logic is separated from provider-specific code so adding GCP or Azure later does not require touching reports or safety rules.

```
janitor/
  core/
    finding.py
    report.py
    policy.py
    pricing.py
  providers/
    aws/
      ec2.py
      ebs.py
      eip.py
      tags.py
```

Each provider translates cloud API responses into a common finding format: resource ID, type, reason, age, tags, estimated cost, suggested action, and `safe_to_auto_delete`.

---

## Permissions

**Dry-run** — read-only. No delete, terminate, or modify permissions.

```json
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
```

**Delete mode** — separate IAM role, tightly scoped, requires explicit approval in production.

---

## Safety Rules

Before any deletion:

- Minimum age threshold must be met
- Resource must not be tagged `Protected=true`
- Resource must not appear in the allowlist

The script recommends first, deletes second. Stopped instances are never auto-deleted.

---

## Observability

| Metric | Alert Condition |
|---|---|
| `janitor_findings_total` | Increases across 3 consecutive runs |
| `estimated_monthly_waste_usd` | Exceeds $100 |
| `untagged_resources_total` | Any production resource missing required tags |
| `janitor_scan_success` | Scan fails |

---

## Current Status

Version 1 covers Terraform baseline and the Janitor script. Multi-cloud providers, production IAM roles, dynamic pricing, and approval workflows are not yet implemented.
