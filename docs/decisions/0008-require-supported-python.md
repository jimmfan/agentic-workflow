# 0008: Require supported runtime and tool floors

- Status: accepted; provider-tool prerequisite superseded by ADR-0018
- Date: 2026-08-13

## Context

The cross-platform, standard-library-only installer originally documented
Python 3.9 as its compatibility floor. Repository history does not record a
feature that specifically requires 3.9; the floor was introduced while the
installer was being made Git-optional and Windows-portable, so it served as a
broad compatibility baseline rather than an exact interpreter pin.

Python 3.9 reached upstream end-of-life on 2025-10-31. Python 3.10 remains in
security support only until 2026-10, which is too little maintenance runway for
a newly released minimum. The framework has no third-party Python dependencies
that constrain a newer interpreter.

The other versioned prerequisites have different roles:

- GitHub CLI 2.90.0 introduced the required public-preview `gh skill` command,
  but GitHub CLI 2.97.0 fixes four security vulnerabilities and its release
  advisory directs users to update. The framework's live compatibility research
  was already performed with 2.97.0.
- `mattpocock/skills` v1.2.3 is an intentionally pinned optional provider
  baseline. It must not float independently of compatibility review.
- Host and provider schema versions are not Python dependency claims.

## Decision

Require Python 3.11 or newer for every executable framework entry point. Treat
3.11 as a minimum compatibility promise,
not an exact pin; development and use may run on newer supported Python 3
releases.

Treat GitHub CLI as a maintainer-only provider snapshot refresh prerequisite,
not a runtime or target-adoption prerequisite. Runtime provider projection is
offline under ADR-0018.

Every entry point must perform the Python version check before network or target
filesystem work and return an actionable ASCII error. User documentation must
distinguish interpreter installation from framework installation and explain
how to verify which interpreter a host or container selects.

## Consequences

- Python 3.9 and 3.10 users must select a supported interpreter before running
  installation, maintenance, verification, or analysis commands.
- Debian 12, Ubuntu 24.04, current macOS package-manager Python, and current
  Windows Python releases satisfy the floor without project dependencies.
- The framework retains its standard-library-only design and adds no package
  manager, virtual environment, lockfile, or third-party runtime dependency.
- Raising the floor again requires a deliberate compatibility decision; an
  upstream end-of-life date alone does not change already installed files.
