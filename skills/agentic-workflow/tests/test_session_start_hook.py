from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = (
    PACKAGE_ROOT
    / "payload"
    / "agent-workflow"
    / "hooks"
    / "inject_route_marker_reminder.py"
)


def load_hook_module():
    spec = importlib.util.spec_from_file_location("inject_route_marker_reminder", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HOOK = load_hook_module()


class SessionStartHookTests(unittest.TestCase):
    def run_hook(self, stdin: str = "") -> dict[str, object]:
        output = io.StringIO()
        original_stdin = sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with redirect_stdout(output):
                HOOK.main()
        finally:
            sys.stdin = original_stdin
        return json.loads(output.getvalue())

    def test_injects_the_one_time_route_marker_reminder(self) -> None:
        self.assertEqual(
            self.run_hook(),
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": HOOK.REMINDER,
                }
            },
        )
        self.assertIn("exactly one truthful final", HOOK.REMINDER)
        self.assertIn("use 'direct'", HOOK.REMINDER)
        self.assertIn("Do not reroute", HOOK.REMINDER)

    def test_does_not_depend_on_host_transcript_or_hook_input(self) -> None:
        self.assertEqual(self.run_hook("not JSON"), self.run_hook())
