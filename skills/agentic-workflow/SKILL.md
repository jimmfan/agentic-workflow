---
name: agentic-workflow
description: Install, update, inspect, or safely remove the repository-native Agentic Workflow payload. Use when adopting the framework into a Git repository or maintaining an existing installation.
license: MIT
---

# Agentic Workflow bootstrap

This skill is the distribution boundary. Its `payload/` directory is the
repository-native workflow installed into a target, while `scripts/adopt.py`
owns safe filesystem changes and `scripts/verify_package.py` validates the
package before any adoption operation.

For a deliberate install request, run the adopter once with `install`; it
performs preflight, applies the payload transactionally, and verifies the result.
Use `--dry-run` only when the user asks for a preview. Do not require a separate
preview, apply, or status command for normal installation.

Lifecycle commands, run from this skill directory or with absolute paths, are:

```bash
python3 scripts/adopt.py install /path/to/repository
python3 scripts/adopt.py update /path/to/repository
python3 scripts/adopt.py status /path/to/repository
python3 scripts/adopt.py remove /path/to/repository
```

Before adoption, validate the distributable package:

```bash
python3 scripts/verify_package.py
```

The public README bootstrap is preferred for end users because it resolves an
immutable GitHub commit and hides the package location. Never bypass conflicts,
edit the target installation manifest to force ownership, or overwrite a
project-owned path.
