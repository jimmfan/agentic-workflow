#!/usr/bin/env python3
"""Install and manage Agent Workflow in a project."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Sequence

if __package__:
    from .scripts import bootstrap
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
    import bootstrap


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return bootstrap.main(argv)
    except bootstrap.BootstrapError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
