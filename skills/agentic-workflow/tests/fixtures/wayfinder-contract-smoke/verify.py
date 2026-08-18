from __future__ import annotations

import json
from pathlib import Path
import re


effort = Path(".agent-workflow-state/wayfinder/runtime-rollout")
mapping = (effort / "map.md").read_text(encoding="utf-8")
evidence = sorted((effort / "evidence").glob("E*.md"))
facts = sorted((effort / "facts").glob("F*.md"))
native_tickets = sorted(Path(".scratch/runtime-rollout/issues").glob("*.md"))
wayfinder_text = "\n".join(
    path.read_text(encoding="utf-8") for path in effort.rglob("*.md")
)

checks = [
    len(evidence) == 1,
    len(facts) == 1,
    "Source: release-policy.txt" in evidence[0].read_text(encoding="utf-8") if evidence else False,
    "## Observation" in evidence[0].read_text(encoding="utf-8") if evidence else False,
    "minimum_supported=3.11" in evidence[0].read_text(encoding="utf-8") if evidence else False,
    "Supported by: E1" in facts[0].read_text(encoding="utf-8") if facts else False,
    "## Fact" in facts[0].read_text(encoding="utf-8") if facts else False,
    not (effort / "unknowns").exists(),
    not (effort / "decisions").exists(),
    not (effort / "tickets").exists(),
    re.search(r"\bT(?:#|[0-9]+)\b", wayfinder_text) is None,
    len(native_tickets) == 3,
    "Blocked by:** None" in native_tickets[0].read_text(encoding="utf-8") if native_tickets else False,
    "Blocked by:** 01" in native_tickets[1].read_text(encoding="utf-8") if len(native_tickets) > 1 else False,
    "Blocked by:** 01" in native_tickets[2].read_text(encoding="utf-8") if len(native_tickets) > 2 else False,
    "02" in native_tickets[2].read_text(encoding="utf-8") if len(native_tickets) > 2 else False,
    ".scratch/runtime-rollout/issues/" in mapping,
    "## Next work" in mapping,
    "01" in mapping,
]
passed = all(checks)
root = Path(".behavior-evidence")
root.mkdir(exist_ok=True)
with (root / "verification.jsonl").open("a", encoding="utf-8") as stream:
    stream.write(
        json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
        + "\n"
    )
print("PASS: Wayfinder contract" if passed else f"FAIL: checks={checks}")
raise SystemExit(0 if passed else 1)
