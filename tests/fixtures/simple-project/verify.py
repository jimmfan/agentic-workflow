from __future__ import annotations

import json
from pathlib import Path

from app import greeting


def main() -> int:
    passed = greeting() == "hello, world!"
    root = Path(".behavior-evidence")
    root.mkdir(exist_ok=True)
    with (root / "verification.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
            + "\n"
        )
    print("PASS: greeting" if passed else "FAIL: greeting")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
