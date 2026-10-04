# ARC Runner Migration

This repository is an in-progress migration of Actions Runner Controller (ARC)
runner capacity onto an existing Amazon EKS platform. Four parallel workstreams
are tracked: W1 runner compute, W2 runner identity/image, W3 legacy-resource
cleanup, and W4 observability/integration.

Use repository evidence carefully:

- current requirements and platform facts are authoritative within their stated scope;
- older architecture notes are retained for history and may be stale;
- a proposal or item under consideration is not an approved decision; and
- resources managed outside this repository must not be recreated or adopted.

Repository changes and local/static validation are authorized. Do not run `terraform init`, `terraform plan`, or provider downloads. `terraform apply` and every other external
infrastructure mutation are not authorized.

Run the repository's offline safety checks with:

```bash
python3 -m unittest discover -s tests -v
```

After implementation changes, run `terraform fmt -check terraform` when Terraform is available.
If Terraform is unavailable, disclose that limitation instead of claiming the formatting check passed.

Save continuation state as Markdown (.md), plain text (.txt), JSON (.json), YAML (.yaml/.yml), or TOML (.toml) files at any repository location outside `terraform/`, `tests/`, installed framework locations, and supplied source documents (including reserved `docs/decisions/` and `docs/benchmarks/` locations).
You may update existing continuation files.
Implementation edits are limited to `terraform/iam.tf`, `terraform/runners.tf`, `terraform/observability.tf`, `terraform/variables.tf`, and `terraform/main.tf` in implementation phases only.
