# ARC Runner Migration

This repository is an in-progress migration of Actions Runner Controller (ARC)
runner capacity onto an existing Amazon EKS platform. The repository contains
current requirements, imported platform facts, stale architecture material, and
incomplete Terraform.

Use repository evidence carefully:

- current requirements and platform facts are authoritative within their stated scope;
- older architecture notes are retained for history and may be stale;
- a proposal or item under consideration is not an approved decision; and
- resources managed outside this repository must not be recreated or adopted.

Repository changes and local/static validation are authorized. A local
`terraform plan` is permitted only if it can run safely without contacting or
changing external infrastructure. `terraform apply` and every other external
infrastructure mutation are not authorized.

Run the repository's offline safety checks with:

```bash
python3 -m unittest discover -s tests -v
```

