# NimbusKart Cost Hygiene Assignment

## Overview

Local DevOps and FinOps assignment for NimbusKart, a fictional e-commerce startup. Provisions AWS-like infrastructure using Terraform and LocalStack, then runs a Python Cost Janitor to detect waste — unattached EBS volumes, stopped EC2 instances, unused Elastic IPs, and missing tags. No real AWS account required.

---

## Prerequisites

```bash
pip install terraform-local
pip install -r janitor/requirements.txt
```

Tools needed: `terraform`, `docker`, `python`, `git`

---

## Running Locally

**Start LocalStack:**

```bash
docker run -d -p 4566:4566 --name localstack localstack/localstack:3.8.1
docker logs localstack --tail 30  # wait for: Ready.
```

**Apply Terraform:**

```bash
cd terraform
tflocal init && tflocal validate && tflocal apply -auto-approve
```

**Run Janitor:**

```bash
cd ..
python janitor/janitor.py --dry-run   # generates report.json + report.md
python janitor/janitor.py --delete    # deletes safe findings, skips Protected=true
```

The script exits non-zero when findings exist. This is intentional — CI should block waste.

---

## Architecture

```
LocalStack (Docker)
  └── Terraform provisions:
        VPC, 2 Subnets, IGW, Route Table, Security Group
        2 EC2 Instances, S3 Logs Bucket, 1 Unattached EBS Volume
  └── Janitor scans and reports:
        report.json + report.md
```

Samples stored in `samples/report.example.json` and `samples/report.example.md`.

---

## Key Decisions

**LocalStack pinned to `3.8.1`** — newer images require license activation.
**AWS provider pinned to `~> 5.0`** — more stable with LocalStack.
**Inline S3 lifecycle config** — separate resource timed out locally.
**SSH open to `0.0.0.0/0`** — assignment default; unsafe in real infrastructure.
**One unattached EBS volume created intentionally** — so the Janitor has something to detect.
**Delete mode is conservative** — only auto-deletes safe findings, always skips `Protected=true`.

---

## AI Usage

Used for planning, debugging Terraform/LocalStack issues, and drafting docs. All commands run and verified manually.
