"""Contract guards for two instruction-loading paths and one skill method.

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


def routing_matrix() -> dict[str, str]:
    routing = read(".agent-workflow/routing.md")
    start = routing.index("<!-- skill-availability-matrix -->")
    end = routing.index("<!-- /skill-availability-matrix -->", start)
    rows: dict[str, str] = {}
    for line in routing[start:end].splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2 or cells[0] in {"Situation", "---"}:
            continue
        rows[cells[0]] = cells[1]
    return rows


@dataclass
class SyntheticHost:
    """Minimal observable host model for deterministic contract scenarios."""

    root: Path
    native_skills: set[str] = field(default_factory=set)
    host_features: set[str] = field(default_factory=lambda: {"repository-read"})
    events: list[str] = field(default_factory=list)

    def instruction_path(self, name: str) -> Path:
        return self.root / ".agents" / "skills" / name / "SKILL.md"

    def read_method(self, name: str) -> tuple[str, str] | None:
        path = self.instruction_path(name)
        if name in self.native_skills:
            self.events.append(f"native-load:{name}")
            return "host-native", path.read_text(encoding="utf-8")
        if "repository-read" not in self.host_features or not path.is_file():
            return None
        self.events.append(f"repository-read:{name}")
        return "repository-read", path.read_text(encoding="utf-8")

    def run_method(
        self,
        name: str,
        *,
        required_host_features: set[str],
        blocking_condition: str | None = None,
        required: bool = True,
    ) -> dict[str, str | bool]:
        loaded = self.read_method(name)
        if loaded is None:
            return self._fallback(name, required, "unavailable", "none")
        instruction_source, instructions = loaded
        missing = required_host_features - self.host_features
        if missing:
            return self._fallback(name, required, "unavailable", instruction_source)
        if blocking_condition is not None:
            if blocking_condition not in {
                "authorization",
                "project-state",
                "required-input",
                "prerequisite",
                "integrity",
            }:
                raise ValueError(f"unsupported synthetic blocker: {blocking_condition}")
            return self._fallback(name, required, "blocked", instruction_source)
        if "PERFORM_SYNTHETIC_METHOD" not in instructions:
            return self._fallback(name, required, "unavailable", instruction_source)
        self.events.append(f"method-executed:{name}")
        return {
            "selected": name,
            "instruction_source": instruction_source,
            "executed": True,
            "method_result": "performed",
            "native_invocation": instruction_source == "host-native",
            "route": name,
        }

    @staticmethod
    def _fallback(
        name: str,
        required: bool,
        outcome: str,
        instruction_source: str,
    ) -> dict[str, str | bool]:
        if not required:
            return {
                "selected": name,
                "instruction_source": instruction_source,
                "executed": False,
                "native_invocation": instruction_source == "host-native",
                "route": "direct",
            }
        return {
            "selected": name,
            "instruction_source": instruction_source,
            "executed": False,
            "native_invocation": instruction_source == "host-native",
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
    def test_routing_matrix_distinguishes_unavailable_from_blocked(self):
        matrix = routing_matrix()

        self.assertEqual(
            matrix["Canonical instructions are missing or unreadable"],
            "unavailable",
        )
        self.assertEqual(
            matrix["A required tool or host feature does not exist or cannot run"],
            "unavailable",
        )
        self.assertEqual(
            matrix[
                "Required support exists and could run, but authorization, project state, a required input or prerequisite, or an integrity condition prevents progress"
            ],
            "blocked",
        )

    def test_both_instruction_loading_paths_converge_on_the_same_method(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root)
            native_host = SyntheticHost(
                root,
                native_skills={"synthetic"},
                host_features={"repository-read", "method-action"},
            )
            repository_host = SyntheticHost(
                root,
                host_features={"repository-read", "method-action"},
            )

            native_result = native_host.run_method(
                "synthetic", required_host_features={"method-action"}
            )
            repository_result = repository_host.run_method(
                "synthetic", required_host_features={"method-action"}
            )

            self.assertEqual(native_result["instruction_source"], "host-native")
            self.assertEqual(repository_result["instruction_source"], "repository-read")
            for field_name in ("selected", "executed", "method_result", "route"):
                self.assertEqual(
                    native_result[field_name], repository_result[field_name]
                )
            self.assertEqual(
                native_host.events,
                ["native-load:synthetic", "method-executed:synthetic"],
            )
            self.assertEqual(
                repository_host.events,
                ["repository-read:synthetic", "method-executed:synthetic"],
            )
            self.assertTrue(native_result["native_invocation"])
            self.assertFalse(repository_result["native_invocation"])

    def test_claude_like_host_uses_agents_policy_and_repository_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root)
            host = SyntheticHost(
                root,
                host_features={"repository-read", "method-action"},
            )
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertFalse(host.native_skills)
            result = host.run_method(
                "synthetic", required_host_features={"method-action"}
            )

            self.assertEqual(result["instruction_source"], "repository-read")
            self.assertTrue(result["executed"])
            self.assertEqual(result["route"], "synthetic")
            self.assertFalse(result["native_invocation"])
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

            result = host.run_method("synthetic", required_host_features=set())

            self.assertFalse(result["executed"])
            self.assertEqual(result["route"], "synthetic-unavailable")
            self.assertEqual(host.events, [])

    def test_missing_parallel_reviewer_support_is_unavailable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root)
            host = SyntheticHost(root)

            result = host.run_method(
                "synthetic", required_host_features={"parallel-reviewers"}
            )

            self.assertFalse(result["executed"])
            self.assertEqual(result["route"], "synthetic-unavailable")
            self.assertEqual(host.events, ["repository-read:synthetic"])

    def test_existing_authorization_condition_blocks_supported_method(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_synthetic_project(root)
            host = SyntheticHost(
                root,
                host_features={"repository-read", "parallel-reviewers"},
            )

            result = host.run_method(
                "synthetic",
                required_host_features={"parallel-reviewers"},
                blocking_condition="authorization",
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
                "synthetic", required_host_features=set(), required=False
            )

            self.assertFalse(result["executed"])
            self.assertEqual(result["route"], "direct")

    def test_host_native_path_loads_canonical_instructions(self):
        routing = read(".agent-workflow/routing.md")

        self.assertIn("through the host's native skill mechanism", routing)
        self.assertIn("Both instruction-loading paths", routing)
        self.assertIn("same selected method", routing)

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
        self.assertIn(
            "read the canonical `.agents/skills/<name>/SKILL.md` directly", routing
        )
        self.assertIn("is not native skill discovery, loading, or invocation", routing)
        self.assertIn(
            "skill descriptions available under the root routing policy", wayfinder
        )
        self.assertNotIn(".agents/skills/<name>/SKILL.md", wayfinder)

    def test_reading_instructions_is_not_execution_and_route_reports_method_only(self):
        routing = read(".agent-workflow/routing.md")

        self.assertIn(
            "selecting it, reading instructions, checking availability", routing
        )
        self.assertIn("does not encode how its instructions were loaded", routing)
        self.assertIn(
            "must not imply native skill discovery, loading, or invocation", routing
        )

    def test_execution_categories_are_not_canonical_terms(self):
        terminology = read(".agent-workflow/terminology.md")
        affected = "\n".join(
            read(path)
            for path in (
                ".agent-workflow/routing.md",
                "docs/architecture.md",
                "README.md",
                "architecture-decisions/0030-use-canonical-skill-methods-without-native-discovery.md",
                "evals/portable-skill-routing/README.md",
            )
        )

        for phrase in ("Native skill execution", "Portable method execution"):
            self.assertNotIn(phrase, terminology)
            self.assertNotIn(phrase.lower(), affected.lower())

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
        self.assertIn(
            "read the canonical `.agents/skills/<name>/SKILL.md` directly", readme
        )
        self.assertIn("does not make `.agents/skills/` a Claude-native", readme)
        self.assertNotIn('"target": ".claude/skills/', manifest)


if __name__ == "__main__":
    unittest.main()
