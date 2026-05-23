# Cost Janitor Report

Scan timestamp: `2026-05-23T23:35:52Z`
Region: `us-east-1`
Total findings: `3`
Estimated monthly waste: `$0.8`

| Resource ID | Type | Reason | Age Days | Cost | Suggested Action | Auto Delete |
|---|---|---|---:|---:|---|---|
| vol-7a317cec | ebs_volume | unattached | 0 | $0.8 | delete | True |
| vol-bb081c60 | ebs_volume | missing_tags:Project,Environment,Owner | 0 | $0.0 | add_required_tags | False |
| vol-ce93fe3d | ebs_volume | missing_tags:Project,Environment,Owner | 0 | $0.0 | add_required_tags | False |
