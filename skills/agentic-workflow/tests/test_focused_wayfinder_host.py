from __future__ import annotations

import json
from pathlib import Path
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
PAYLOAD_AGENT = PACKAGE_ROOT / "payload/agents/vscode-wayfinder.agent.md"
INSTALLED_AGENT = REPOSITORY_ROOT / ".github/agents/wayfinder.agent.md"
HOOK_CONFIG = PACKAGE_ROOT / "payload/hooks/vscode-route-marker.json"
MANIFEST = PACKAGE_ROOT / "payload/distribution/manifest.json"


class FocusedWayfinderHostTests(unittest.TestCase):
    def test_vscode_projection_is_thin_capability_limited_and_canonical(self) -> None:
        payload = PAYLOAD_AGENT.read_text(encoding="utf-8")
        self.assertEqual(payload, INSTALLED_AGENT.read_text(encoding="utf-8"))
        self.assertTrue(payload.startswith("---\n"))
        _, frontmatter, body = payload.split("---\n", 2)

        self.assertIn("name: Wayfinder", frontmatter)
        self.assertIn("tools: ['read', 'search', 'edit', 'execute']", frontmatter)
        self.assertIn("agents: []", frontmatter)
        self.assertIn("disable-model-invocation: true", frontmatter)
        self.assertIn("target: vscode", frontmatter)
        self.assertNotIn("web", frontmatter)
        self.assertNotIn("agent'", frontmatter)

        normalized = " ".join(body.split())
        self.assertLessEqual(len(body.split()), 180)
        self.assertIn(".agents/skills/wayfinder/SKILL.md", normalized)
        self.assertIn(".agent-workflow/contracts/wayfinder-state.md", normalized)
        self.assertIn(
            "domain → active territory → relevant architecture → necessary implementation detail",
            normalized,
        )
        self.assertIn("sole framework-owned writer", normalized)
        self.assertIn("Use `execute` only to create and remove", normalized)
        self.assertIn("atomic mutation lock directory", normalized)
        self.assertIn("Do not use the terminal to write or delete durable state", normalized)
        self.assertIn("ready frontier", normalized)
        self.assertIn("human/project authority", normalized)
        for metaphor in ("project manager", "employee", "specialist manager"):
            self.assertNotIn(metaphor, normalized.casefold())

    def test_distribution_installs_agent_and_preserves_phase_zero_hook(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mappings = {
            item["target"]: item["source"] for item in manifest["framework_owned"]
        }
        self.assertEqual(
            mappings[".github/agents/wayfinder.agent.md"],
            "agents/vscode-wayfinder.agent.md",
        )
        self.assertEqual(
            mappings[".agent-workflow/hooks/protect_wayfinder_state.py"],
            "agent-workflow/hooks/protect_wayfinder_state.py",
        )

        config = json.loads(HOOK_CONFIG.read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(
            config["SessionStart"],
            [
                {
                    "type": "command",
                    "command": "python3 .agent-workflow/hooks/inject_route_marker_reminder.py",
                    "windows": "py -3 .agent-workflow\\hooks\\inject_route_marker_reminder.py",
                    "timeout": 5,
                }
            ],
        )
        self.assertEqual(
            config["PreToolUse"],
            [
                {
                    "type": "command",
                    "command": "python3 .agent-workflow/hooks/protect_wayfinder_state.py",
                    "windows": "py -3 .agent-workflow\\hooks\\protect_wayfinder_state.py",
                    "timeout": 5,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
