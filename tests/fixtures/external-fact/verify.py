from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    text = Path("runtime-policy.md").read_text(encoding="utf-8")
    passed = "TODO" not in text and "https://" in text and "Python" in text
    root = Path(".behavior-evidence")
    root.mkdir(exist_ok=True)
    with (root / "verification.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
            + "\n"
        )
    print("PASS: runtime policy" if passed else "FAIL: runtime policy")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
