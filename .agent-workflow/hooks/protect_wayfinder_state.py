#!/usr/bin/env python3
"""Deny explicit apply_patch deletion of a current Wayfinder effort map."""

from __future__ import annotations

import json
import re
import sys
from typing import Any


STATE_ROOT = ".agent-workflow-state/wayfinder"
DELETE_FILE_LINE = re.compile(r"^\s*\*\*\*\s+Delete File:\s*(.+?)\s*$", re.MULTILINE)
DENIAL_REASON = (
    "A Wayfinder effort map cannot be deleted silently; reconcile its current "
    "state and lifecycle in place."
)


def targets_wayfinder_effort_map(value: object) -> bool:
    if not isinstance(value, str):
        return False
    candidate = value.strip().strip("'\"").replace("\\", "/")
    bounded = f"/{candidate.strip('/')}/"
    marker = f"/{STATE_ROOT}/"
    marker_index = bounded.find(marker)
    if marker_index < 0:
        return False
    relative = bounded[marker_index + len(marker) :].strip("/")
    parts = relative.split("/")
    return len(parts) == 2 and parts[0] not in {".", "..", ""} and parts[1] == "map.md"


def apply_patch_deletes_state(tool_input: object) -> bool:
    if not isinstance(tool_input, dict):
        return False
    patch = tool_input.get("input")
    if not isinstance(patch, str):
        return False
    return any(targets_wayfinder_effort_map(match) for match in DELETE_FILE_LINE.findall(patch))


def should_deny(payload: object) -> bool:
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "PreToolUse":
        return False
    if payload.get("tool_name") != "apply_patch":
        return False
    return apply_patch_deletes_state(payload.get("tool_input"))


def denial_output() -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": DENIAL_REASON,
        }
    }


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return
    if should_deny(payload):
        json.dump(denial_output(), sys.stdout, separators=(",", ":"))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
