from __future__ import annotations

import importlib.util
from io import StringIO
import json
from pathlib import Path
import sys
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = PACKAGE_ROOT / "payload/agent-workflow/hooks/protect_wayfinder_state.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("protect_wayfinder_state", GUARD_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PreToolUseGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guard = load_guard()

    def run_guard_raw(self, value: str) -> str:
        original_stdin = sys.stdin
        original_stdout = sys.stdout
        sys.stdin = StringIO(value)
        sys.stdout = output = StringIO()
        try:
            self.guard.main()
        finally:
            sys.stdin = original_stdin
            sys.stdout = original_stdout
        return output.getvalue()

    def run_guard(self, payload: object) -> str:
        return self.run_guard_raw(json.dumps(payload))

    def test_allows_normal_wayfinder_reconciliation(self) -> None:
        output = self.run_guard(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "input": "*** Begin Patch\n*** Update File: .agent-workflow-state/wayfinder/example/map.md\n@@\n-old\n+current\n*** End Patch"
                },
            }
        )
        self.assertEqual(output, "")

    def test_denies_explicit_effort_map_deletion(self) -> None:
        output = self.run_guard(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "input": "*** Begin Patch\n*** Delete File: .agent-workflow-state/wayfinder/example/map.md\n*** End Patch"
                },
            }
        )
        self.assertEqual(
            json.loads(output),
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "A Wayfinder effort map cannot be deleted silently; reconcile its current "
                        "state and lifecycle in place."
                    ),
                }
            },
        )

    def test_denies_windows_style_delete_targeting_the_state_root(self) -> None:
        output = self.run_guard(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "input": "*** Delete File: C:\\repo\\.agent-workflow-state\\wayfinder\\example\\map.md"
                },
            }
        )
        self.assertEqual(json.loads(output)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_allows_contract_valid_child_retirement(self) -> None:
        for path in (
            ".agent-workflow-state/wayfinder/example/unknowns/U1-resolved.md",
            ".agent-workflow-state/wayfinder/example/notes/map.md",
        ):
            with self.subTest(path=path):
                output = self.run_guard(
                    {
                        "hook_event_name": "PreToolUse",
                        "tool_name": "apply_patch",
                        "tool_input": {"input": f"*** Delete File: {path}"},
                    }
                )
                self.assertEqual(output, "")

    def test_ignores_other_tools_malformed_input_and_unrelated_deletes(self) -> None:
        cases = (
            "not JSON",
            {"hook_event_name": "PostToolUse", "tool_name": "apply_patch", "tool_input": {}},
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "vendor_apply_patch",
                "tool_input": {
                    "input": "*** Delete File: .agent-workflow-state/wayfinder/example/map.md"
                },
            },
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "apply_patch",
                "tool_input": {"input": "*** Delete File: src/obsolete.py"},
            },
        )
        for payload in cases:
            with self.subTest(payload=payload):
                if isinstance(payload, str):
                    self.assertEqual(self.run_guard_raw(payload), "")
                else:
                    self.assertEqual(self.run_guard(payload), "")


if __name__ == "__main__":
    unittest.main()
