from __future__ import annotations

import json
from pathlib import Path

from slug import slugify


def main() -> int:
    cases = {
        " Hello, World! ": "hello-world",
        "Already--Spaced": "already-spaced",
        "___": "",
    }
    try:
        passed = all(slugify(value) == expected for value, expected in cases.items())
    except Exception:
        passed = False
    root = Path(".behavior-evidence")
    root.mkdir(exist_ok=True)
    with (root / "verification.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
            + "\n"
        )
    print("PASS: slugify" if passed else "FAIL: slugify")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
