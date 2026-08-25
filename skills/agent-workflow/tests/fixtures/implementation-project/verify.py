from __future__ import annotations

import json
from pathlib import Path

from config import parse_bool


def main() -> int:
    passed = True
    try:
        passed = passed and all(parse_bool(value) for value in ("true", "YES", " 1 "))
        passed = passed and not any(
            parse_bool(value) for value in ("false", "No", " 0 ")
        )
        try:
            parse_bool("sometimes")
        except ValueError:
            pass
        else:
            passed = False
    except Exception:
        passed = False
    root = Path(".behavior-evidence")
    root.mkdir(exist_ok=True)
    with (root / "verification.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
            + "\n"
        )
    print("PASS: parse_bool" if passed else "FAIL: parse_bool")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
