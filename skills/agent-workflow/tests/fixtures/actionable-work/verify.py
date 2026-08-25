from __future__ import annotations

import json
from pathlib import Path

from pricing import bounded_discount


def main() -> int:
    try:
        passed = [bounded_discount(value) for value in (-5, 25, 140)] == [0, 25, 100]
    except Exception:
        passed = False
    root = Path(".behavior-evidence")
    root.mkdir(exist_ok=True)
    with (root / "verification.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
            + "\n"
        )
    print("PASS: discount bounds" if passed else "FAIL: discount bounds")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
