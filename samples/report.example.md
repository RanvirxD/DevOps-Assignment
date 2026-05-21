# Cost Janitor Report

Scan timestamp: `2026-05-21T19:38:28Z`
Region: `us-east-1`
Total findings: `3`
Estimated monthly waste: `$0.8`

| Resource ID | Type | Reason | Age Days | Cost | Suggested Action |
|---|---|---|---:|---:|---|
| vol-366dca93 | ebs_volume | unattached | 0 | $0.8 | delete |
| vol-2dd6299e | ebs_volume | missing_tags:Project,Environment,Owner | 0 | $0.0 | add_required_tags |
| vol-4d3bb98c | ebs_volume | missing_tags:Project,Environment,Owner | 0 | $0.0 | add_required_tags |
