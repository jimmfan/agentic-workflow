"""Contract guards for native and repository-read skill execution paths.

These tests inspect distributed instructions and synthetic host outcomes. They do
not claim that a live model followed the instructions or that a host discovered
``.agents/skills`` natively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def routing_matrix() -> dict[tuple[str, str, str], str]:
    routing = read(".agent-workflow/routing.md")
    start = routing.index("<!-- portable-skill-routing-matrix -->")
    end = routing.index("<!-- /portable-skill-routing-matrix -->", start)
    rows: dict[tuple[str, str, str], str] = {}
    for line in routing[start:end].splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0] in {"Native exposure", "---"}:
            continue
        rows[tuple(cells[:3])] = cells[3]
    return rows


@dataclass
class SyntheticHost:
    """Minimal observable host model for deterministic contract scenarios."""

    root: Path
    native_skills: set[str] = field(default_factory=set)
    capabilities: set[str] = field(default_factory=lambda: {"repository-read"})
    events: list[str] = field(default_factory=list)

    def instruction_path(self, name: str) -> Path:
        return self.root / ".agents" / "skills" / name / "SKILL.md"

    def read_method(self, name: str) -> tuple[str, str] | None:
        path = self.instruction_path(name)
        if name in self.native_skills:
            self.events.append(f"native-load:{name}")
            return "native", path.read_text(encoding="utf-8")
        if "repository-read" not in self.capabilities or not path.is_file():
            return None
        self.events.append(f"repository-read:{name}")
        return "portable", path.read_text(encoding="utf-8")

    def run_method(
        self,
        name: str,
        *,
        required_capabilities: set[str],
        required: bool = True,
    ) -> dict[str, str | bool]:
        loaded = self.read_method(name)
        if loaded is None:
            return self._fallback(name, required, "unavailable")
        instruction_source, instructions = loaded
        missing = required_capabilities - self.capabilities
        if missing:
            return self._fallback(name, required, "blocked")
        if "PERFORM_SYNTHETIC_METHOD" not in instructions:
            return self._fallback(name, required, "unavailable")
        self.events.append(f"method-executed:{name}")
        return {
            "selected": name,
            "instruction_source": instruction_source,
            "executed": True,
            "route": name,
        }

    @staticmethod
    def _fallback(name: str, required: bool, outcome: str) -> dict[str, str | bool]:
        if not required:
            return {
                "selected": name,
                "instruction_source": "none",
                "executed": False,
                "route": "direct",
            }
        return {
            "selected": name,
            "instruction_source": "none",
            "executed": False,
            "route": f"{name}-{outcome}",
        }


def make_synthetic_project(root: Path, *, include_skill: bool = True) -> None:
    (root / "AGENTS.md").write_text(
        read("agent_workflow/install/AGENTS.md.template"), encoding="utf-8"
    )
    if include_skill:
        skill = root / ".agents" / "skills" / "synthetic" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(
            "---\nname: synthetic\ndescription: Exercise a synthetic method.\n---\n"
            "PERFORM_SYNTHETIC_METHOD\n",
            encoding="utf-8",
        )


class PortableSkillRoutingTests(unittest.TestCase):
    def test_synthetic_host_outcomes_cover_both_execution_paths_and_failures(self):
        matrix = routing_matrix()

        self.assertEqual(
            matrix[("exposed", "host-loaded", "available")],
            "native skill execution",
        )
        self.assertEqual(
            matrix[("not exposed", "readable", "available")],
            "portable method execution",
        )
        self.assertEqual(
            matrix[("not exposed", "missing or unreadable", "any")],
            "unavailable",
        )
        self.assertEqual(
            matrix[("not exposed", "readable", "required capability unavailable")],
            "unavailable or blocked",
        )

    def test_native_exposed_skill_uses_host_load_and_executes_canonical_method(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root)
            host = SyntheticHost(
                root,
                native_skills={"synthetic"},
                capabilities={"repository-read", "method-action"},
            )

            result = host.run_method(
                "synthetic", required_capabilities={"method-action"}
            )

            self.assertEqual(result["instruction_source"], "native")
            self.assertTrue(result["executed"])
            self.assertEqual(
                host.events,
                ["native-load:synthetic", "method-executed:synthetic"],
            )

    def test_claude_like_host_reads_and_executes_portable_method_without_native_claim(
        self,
    ):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root)
            host = SyntheticHost(
                root,
                capabilities={"repository-read", "method-action"},
            )

            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertFalse(host.native_skills)
            result = host.run_method(
                "synthetic", required_capabilities={"method-action"}
            )

            self.assertEqual(result["instruction_source"], "portable")
            self.assertTrue(result["executed"])
            self.assertEqual(result["route"], "synthetic")
            self.assertEqual(
                host.events,
                ["repository-read:synthetic", "method-executed:synthetic"],
            )
            self.assertFalse(
                any(event.startswith("native-load:") for event in host.events)
            )

    def test_missing_canonical_file_is_unavailable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root, include_skill=False)
            host = SyntheticHost(root)

            result = host.run_method("synthetic", required_capabilities=set())

            self.assertFalse(result["executed"])
            self.assertEqual(result["route"], "synthetic-unavailable")
            self.assertEqual(host.events, [])

    def test_missing_required_capability_blocks_after_read_without_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root)
            host = SyntheticHost(root)

            result = host.run_method(
                "synthetic", required_capabilities={"parallel-reviewers"}
            )

            self.assertFalse(result["executed"])
            self.assertEqual(result["route"], "synthetic-blocked")
            self.assertEqual(host.events, ["repository-read:synthetic"])

    def test_merely_reading_does_not_count_as_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root)
            host = SyntheticHost(root)

            loaded = host.read_method("synthetic")

            self.assertIsNotNone(loaded)
            self.assertEqual(host.events, ["repository-read:synthetic"])
            self.assertFalse(
                any(event.startswith("method-executed:") for event in host.events)
            )

    def test_optional_unavailable_skill_falls_back_to_direct(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root, include_skill=False)
            host = SyntheticHost(root)

            result = host.run_method(
                "synthetic", required_capabilities=set(), required=False
            )

            self.assertFalse(result["executed"])
            self.assertEqual(result["route"], "direct")

    def test_native_path_remains_preferred_and_uses_canonical_instructions(self):
        routing = read(".agent-workflow/routing.md")

        self.assertIn("When the host exposes the selected skill natively", routing)
        self.assertIn("use its native skill mechanism", routing)
        self.assertIn("installed canonical instructions", routing)

    def test_repository_read_path_is_selection_input_and_not_native_invocation(self):
        routing = read(".agent-workflow/routing.md")
        distributed_root = read("agent_workflow/install/AGENTS.md.template")
        source_root = read("AGENTS.md")
        wayfinder = read(".agents/skills/wayfinder/SKILL.md")

        for policy in (distributed_root, source_root):
            self.assertIn(".agents/skills/<name>/SKILL.md", policy)
            self.assertIn(
                "does not expose an applicable Agent Workflow skill natively",
                policy,
            )
        self.assertIn("execute the portable parts of its method directly", routing)
        self.assertIn("not native host skill invocation", routing)
        self.assertIn("readable canonical `.agents/skills/<name>/SKILL.md`", wayfinder)

    def test_reading_instructions_is_not_execution_and_route_reports_method_only(self):
        routing = read(".agent-workflow/routing.md")

        self.assertIn(
            "selecting it, reading instructions, checking availability", routing
        )
        self.assertIn("does not encode which instruction-loading path ran", routing)
        self.assertIn("must not imply native skill invocation", routing)

    def test_optional_skill_can_still_fall_back_to_direct(self):
        routing = read(".agent-workflow/routing.md")

        self.assertIn(
            "continue Direct only when the user did not require that skill", routing
        )
        self.assertIn(
            "After a successful Direct fallback, omit the skill that could not run",
            routing,
        )

    def test_claude_like_host_uses_agents_policy_without_claude_skill_duplication(self):
        readme = read("README.md")
        manifest = read("agent_workflow/install/manifest.json")

        self.assertIn("Claude Code", readme)
        self.assertIn("reads the canonical `.agents/skills/<name>/SKILL.md`", readme)
        self.assertIn("does not make `.agents/skills/` a Claude-native", readme)
        self.assertNotIn('"target": ".claude/skills/', manifest)


if __name__ == "__main__":
    unittest.main()
