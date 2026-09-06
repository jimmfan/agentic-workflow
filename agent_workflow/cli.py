#!/usr/bin/env python3
"""Install and manage Agent Workflow in a project."""

from __future__ import annotations

import sys
from typing import Sequence

if __package__:
    from . import bootstrap
else:
    import bootstrap


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return bootstrap.main(argv)
    except bootstrap.BootstrapError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
