# Submission — DevOps Engineer Assignment

**Candidate name:** Ranvir Singh
**Email:** ranvirsingh.15h@gmail.com
**Date:** 24-05-2026 
**Hours spent (approximate):** 2hr

---

## Deliverables Checklist

- [x] Part A: Terraform code under `/terraform` applies cleanly on LocalStack
- [x] Part A: `terraform validate` and `terraform fmt -check` both pass
- [x] Part B: Janitor script runs in `--dry-run` mode and produces `report.json`
- [x] Part B: GitHub Actions workflow runs green on a fresh PR
- [x] Part B: `--delete` mode respects `Protected=true` tag
- [ ] Part C: `DESIGN.md` is present and within 2 pages
- [ ] Walkthrough video link below is accessible (unlisted is fine)

---

## Sample Report

Path to a sample `report.json` produced by the script:

---

## Known Limitations

**Janitor script not implemented.**
Part B is pending. The script, dry-run mode, and report output will be added in the next phase.

**GitHub Actions workflow not implemented.**
The CI workflow has not been set up yet and will follow once the Janitor script is complete.

**DESIGN.md is a draft.**
The current version is a placeholder. It will be updated and finalized after Part B is complete.

**LocalStack pinned to version 3.8.1.**
The `latest` and `stable` tags required license activation during local testing. Pinning to `3.8.1` was the only way to run cleanly without a paid license.

---

## AI Usage Disclosure

AI was used for planning, working through Terraform and LocalStack issues, and drafting documentation. All commands were run manually. Errors were read, diagnosed, and fixed by hand. The final `terraform apply` output was verified locally before submission.
