# Submission — DevOps Engineer Assignment

**Candidate name:** Ranvir Singh
**Email:** ranvirsingh.15h@gmail.com
**Date submitted:** 24/05/2026
**Hours spent (approximate):** 4hrs 

---

## Deliverables Checklist

- [x] Part A: Terraform applies cleanly on LocalStack
- [x] Part A: `terraform validate` and `terraform fmt -check` pass
- [x] Part B: Janitor runs in `--dry-run` mode and produces `report.json`
- [x] Part B: GitHub Actions workflow runs end-to-end (fails intentionally when findings exist)
- [x] Part B: `--delete` mode respects `Protected=true`
- [x] Part C: `DESIGN.md` present and within 2 pages
- [ ] Walkthrough video accessible

---

## Walkthrough Video

Link:
Length: under 5 minutes

---

## Sample Report

`samples/report.example.json`

---

## Known Limitations

**LocalStack only** — no real AWS account; some behavior is simulated.
**Static pricing** — not pulled from the AWS Pricing API.
**Stopped EC2 age** — based on available metadata, not full state transition history.
**CI fails on findings** — intentional; dry-run exits non-zero when waste is detected.

---

## AI Usage

Used for planning, debugging, and drafting docs. Commands, outputs, and delete behavior verified manually.
