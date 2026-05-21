"""
Pricing constants used by the Cost Janitor.

These are simple static estimates for local assignment use.
Source reference:
AWS EBS gp3 pricing is commonly listed around $0.08 per GB-month in us-east-1.
Actual production pricing should be pulled from the AWS Pricing API.
"""

REQUIRED_TAGS = ["Project", "Environment", "Owner"]

DEFAULT_REGION = "us-east-1"
DEFAULT_ACCOUNT_ID = "000000000000"

LOCALSTACK_ENDPOINT = "http://localhost:4566"

PRICING = {
    "ebs_gp3_gb_month": 0.08,
    "elastic_ip_month": 3.60,
    "stopped_t3_micro_month": 0.00
}