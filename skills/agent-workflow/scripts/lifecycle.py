#!/usr/bin/env python3
"""Run the direct Agent Workflow install, update, status, and remove lifecycle."""

from __future__ import annotations

from typing import Iterable

import adopt


def main(argv: Iterable[str] | None = None) -> int:
    return adopt.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
