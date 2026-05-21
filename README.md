# NimbusKart Cost Hygiene Assignment

## Overview

A local DevOps and FinOps assignment for NimbusKart, a fictional e-commerce startup. The goal is to simulate AWS-like infrastructure locally using Terraform and LocalStack, then build automation to detect cloud waste — unattached EBS volumes, stopped instances, unused Elastic IPs, and missing tags.

**Current status:** Version 1 completes the Terraform baseline infrastructure.

---

## Prerequisites

Make sure the following tools are installed before proceeding:

- `terraform`
- `docker`
- `python`
- `git`

Install the LocalStack Terraform wrapper:

```bash
pip install terraform-local
```

---

## Running Locally

**Clone the repository:**

```bash
git clone https://github.com/RanvirxD/DevOps-Assignment
cd DevOps-Assignment
```

**Start LocalStack:**

```bash
docker run -d -p 4566:4566 --name localstack localstack/localstack:3.8.1
docker logs localstack --tail 30
```

Expected log output:

```
Ready.
```

**Run Terraform:**

```bash
cd terraform
terraform fmt -recursive
tflocal init
tflocal validate
tflocal apply -auto-approve
```

Expected output:

```
bucket_name      = "nimbuskart-staging-app-logs"
public_subnet_ids = [...]
vpc_id           = "vpc-..."
```

---

## Resetting LocalStack

To wipe and restart LocalStack cleanly:

```bash
docker rm -f localstack
docker run -d -p 4566:4566 --name localstack localstack/localstack:3.8.1
```

---

## Infrastructure Layout

```
Developer Machine
      |
      | Terraform via tflocal
      v
LocalStack (Docker)
      |
      v
NimbusKart Staging Infra
      |
      |-- VPC: 10.20.0.0/16
      |-- 2 Public Subnets
      |-- Internet Gateway
      |-- Public Route Table
      |-- Security Group
      |-- 2 EC2 Web Instances
      |-- S3 Logs Bucket
      |-- 1 Unattached EBS Volume (intentional, for Janitor script)
```

---

## Decisions and Deviations

**LocalStack version pinned to `3.8.1`.**
The `latest` and `stable` tags required license activation during local testing. Pinning to `3.8.1` avoids this.

**AWS provider pinned to `~> 5.0`.**
This version worked more reliably with LocalStack than newer alternatives.

**Inline S3 versioning and lifecycle configuration.**
The separate lifecycle resource consistently timed out in local testing, so configuration was moved inline.

**SSH open to `0.0.0.0/0`.**
This follows the assignment default. In real infrastructure this must be restricted to trusted CIDR ranges.

**One unattached EBS volume created intentionally.**
This serves as a detectable waste resource for the Janitor script in a future phase.

**Placeholder AMI used.**
LocalStack does not require a real AWS AMI for local simulation, so a placeholder is sufficient.
