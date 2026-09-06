from __future__ import annotations

import json
from pathlib import Path

from service import serialize_payload


def main() -> int:
    try:
        actual = serialize_payload({"b": 2, "a": 1})
    except Exception:
        actual = ""
    passed = actual == '{"a":1,"b":2}'
    root = Path(".behavior-evidence")
    root.mkdir(exist_ok=True)
    with (root / "verification.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
            + "\n"
        )
    print(
        "PASS: serialization" if passed else f"FAIL: serialization returned {actual!r}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
