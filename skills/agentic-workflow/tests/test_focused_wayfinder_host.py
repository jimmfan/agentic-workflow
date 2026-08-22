from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
PAYLOAD_AGENT = PACKAGE_ROOT / "payload/agents/vscode-wayfinder.agent.md"
INSTALLED_AGENT = REPOSITORY_ROOT / ".github/agents/wayfinder.agent.md"
PARENT_INSTRUCTIONS = (
    PACKAGE_ROOT / "payload/root/vscode-copilot-instructions.md.template"
)
INSTALLED_PARENT_INSTRUCTIONS = REPOSITORY_ROOT / ".github/copilot-instructions.md"
HOOK_CONFIG = PACKAGE_ROOT / "payload/hooks/vscode-route-marker.json"
MANIFEST = PACKAGE_ROOT / "payload/distribution/manifest.json"
ADOPT = PACKAGE_ROOT / "scripts/adopt.py"
MANAGED_BEGIN = "<!-- agent-workflow:managed-begin -->\n"
MANAGED_END = "<!-- agent-workflow:managed-end -->\n"


def frontmatter_fields(payload: str) -> dict[str, str]:
    _, frontmatter, _ = payload.split("---\n", 2)
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def run_adopt(script: Path, command: str, project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), command, str(project)],
        text=True,
        capture_output=True,
    )


class FocusedWayfinderHostTests(unittest.TestCase):
    def assert_model_and_user_invocable(self, agent: Path) -> None:
        fields = frontmatter_fields(agent.read_text(encoding="utf-8"))
        self.assertEqual(fields.get("disable-model-invocation"), "false")
        self.assertEqual(fields.get("user-invocable"), "true")

    def test_vscode_projection_is_model_and_user_invocable(self) -> None:
        payload = PAYLOAD_AGENT.read_text(encoding="utf-8")
        self.assertEqual(payload, INSTALLED_AGENT.read_text(encoding="utf-8"))
        self.assert_model_and_user_invocable(PAYLOAD_AGENT)

    def test_vscode_parent_instruction_requires_focused_invocation_and_result_consumption(self) -> None:
        expected = PARENT_INSTRUCTIONS.read_text(encoding="utf-8").rstrip("\n") + "\n"
        installed = INSTALLED_PARENT_INSTRUCTIONS.read_text(encoding="utf-8")
        self.assertTrue(installed.startswith(MANAGED_BEGIN))
        managed_end = installed.index(MANAGED_END)
        self.assertEqual(installed[len(MANAGED_BEGIN):managed_end], expected)

        normalized = " ".join(expected.split())
        self.assertIn("semantic routing selects Wayfinder", normalized)
        self.assertIn("invoke that exact agent as a subagent", normalized)
        self.assertIn("instead of loading or executing the Wayfinder skill inline", normalized)
        self.assertIn("consume its coordination result", normalized)
        self.assertIn("Do not substantially repeat", normalized)
        for exception in ("missing evidence", "conflicts", "lacks support"):
            self.assertIn(exception, normalized)
        for negative_route in ("Direct", "Debugging"):
            self.assertIn(negative_route, normalized)
        self.assertIn("model invocation is disabled", normalized)
        self.assertIn("portable Wayfinder path", normalized)

    def test_invocation_contract_rejects_disabled_temporary_variant(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            disabled = Path(temporary) / "wayfinder.agent.md"
            disabled.write_text(
                PAYLOAD_AGENT.read_text(encoding="utf-8").replace(
                    "disable-model-invocation: false",
                    "disable-model-invocation: true",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(AssertionError, "'true' != 'false'"):
                self.assert_model_and_user_invocable(disabled)

    def test_vscode_projection_is_thin_capability_limited_and_canonical(self) -> None:
        payload = PAYLOAD_AGENT.read_text(encoding="utf-8")
        self.assertTrue(payload.startswith("---\n"))
        _, frontmatter, body = payload.split("---\n", 2)
        fields = frontmatter_fields(payload)

        self.assertIn("name: Wayfinder", frontmatter)
        self.assertIn("durable project understanding", fields["description"])
        for signal in ("unknowns", "decisions", "dependencies", "blockers", "handoffs"):
            self.assertIn(signal, fields["description"])
        self.assertIn("tools: ['read', 'search', 'edit', 'execute']", frontmatter)
        self.assertIn("agents: []", frontmatter)
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
        for relative in (
            "../../.agents/skills/wayfinder/SKILL.md",
            "../../.agent-workflow/contracts/wayfinder-state.md",
        ):
            self.assertTrue(
                (INSTALLED_AGENT.parent / relative).resolve().is_file(),
                f"focused Wayfinder canonical link is missing: {relative}",
            )
        for metaphor in ("project manager", "employee", "specialist manager"):
            self.assertNotIn(metaphor, normalized.casefold())

    def test_portable_routing_does_not_absorb_vscode_invocation_mechanics(self) -> None:
        portable = "\n".join(
            [
                (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text(encoding="utf-8"),
                (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text(encoding="utf-8"),
                (PACKAGE_ROOT / "runtime-projections/wayfinder.md").read_text(encoding="utf-8"),
            ]
        )
        for host_detail in (
            "disable-model-invocation",
            "user-invocable",
            ".github/agents",
            "vscode-wayfinder.agent.md",
        ):
            self.assertNotIn(host_detail, portable)

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
            mappings[".github/copilot-instructions.md"],
            "root/vscode-copilot-instructions.md.template",
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

    def test_update_enables_phase_two_agent_and_preserves_state_and_unrelated_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            state = project / ".agent-workflow-state/wayfinder/human-owned/map.md"
            state.parent.mkdir(parents=True)
            state.write_bytes(b"# Human-owned state\n\nKeep byte-for-byte.\n")
            unrelated = project / ".github/agents/local-reviewer.agent.md"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_bytes(b"---\nname: Local reviewer\n---\n\nKeep me.\n")
            expected_state = b"# Human-owned state\n\nKeep byte-for-byte.\n"
            expected_unrelated = b"---\nname: Local reviewer\n---\n\nKeep me.\n"
            copilot_instructions = project / ".github/copilot-instructions.md"
            copilot_instructions.write_bytes(b"# Project Copilot policy\n\nKeep byte-for-byte.\n")
            expected_copilot_project = b"# Project Copilot policy\n\nKeep byte-for-byte.\n"

            def assert_human_files_preserved() -> None:
                self.assertEqual(state.read_bytes(), expected_state)
                self.assertEqual(unrelated.read_bytes(), expected_unrelated)
                self.assertTrue(copilot_instructions.read_bytes().endswith(expected_copilot_project))

            old_package = root / "old-package"
            shutil.copytree(PACKAGE_ROOT, old_package)
            old_agent = old_package / "payload/agents/vscode-wayfinder.agent.md"
            old_payload = old_agent.read_text(encoding="utf-8")
            old_payload = old_payload.replace(
                "user-invocable: true\n",
                "",
            ).replace(
                "disable-model-invocation: false",
                "disable-model-invocation: true",
            )
            old_agent.write_text(old_payload, encoding="utf-8")

            installed = run_adopt(old_package / "scripts/adopt.py", "install", project)
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            projected = project / ".github/agents/wayfinder.agent.md"
            self.assertIn("disable-model-invocation: true", projected.read_text())

            for command in ("update", "update"):
                result = run_adopt(ADOPT, command, project)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                fields = frontmatter_fields(projected.read_text(encoding="utf-8"))
                self.assertEqual(fields["user-invocable"], "true")
                self.assertEqual(fields["disable-model-invocation"], "false")
                assert_human_files_preserved()

            removed = run_adopt(ADOPT, "remove", project)
            self.assertEqual(removed.returncode, 0, removed.stdout + removed.stderr)
            self.assertFalse(projected.exists())
            self.assertEqual(copilot_instructions.read_bytes(), expected_copilot_project)
            self.assertEqual(state.read_bytes(), expected_state)
            self.assertEqual(unrelated.read_bytes(), expected_unrelated)

            reinstalled = run_adopt(ADOPT, "install", project)
            self.assertEqual(reinstalled.returncode, 0, reinstalled.stdout + reinstalled.stderr)
            fields = frontmatter_fields(projected.read_text(encoding="utf-8"))
            self.assertEqual(fields["user-invocable"], "true")
            self.assertEqual(fields["disable-model-invocation"], "false")
            assert_human_files_preserved()


if __name__ == "__main__":
    unittest.main()
