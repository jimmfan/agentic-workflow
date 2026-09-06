from __future__ import annotations

import json
import re
from pathlib import Path


def main() -> int:
    text = Path("runtime-policy.md").read_text(encoding="utf-8")
    # This checks report structure, not which changing release is currently stable.
    passed = (
        "TODO" not in text
        and re.search(r"Python 3\.[0-9]+", text) is not None
        and re.search(r"\b(?:bugfix|security|end.of.life)\b", text, re.IGNORECASE)
        is not None
        and "https://www.python.org/" in text
    )
    root = Path(".behavior-evidence")
    root.mkdir(exist_ok=True)
    with (root / "verification.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
            + "\n"
        )
    print(
        "PASS: runtime policy structure; current factual accuracy requires adjudication"
        if passed
        else "FAIL: runtime policy"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
