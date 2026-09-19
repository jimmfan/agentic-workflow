"""Structural guards for canonical repository-read skill references.

This check covers canonical references, not instruction meaning or live host
behavior. Review covers the prose; the opt-in Claude protocol covers compliance.
"""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PortableSkillRoutingTests(unittest.TestCase):
    def test_selection_and_loading_policies_reference_the_canonical_skill_path(self):
        for relative in (
            "AGENTS.md",
            "agent_workflow/install/AGENTS.md.template",
            ".agent-workflow/routing.md",
        ):
            with self.subTest(policy=relative):
                policy = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(".agents/skills/<name>/SKILL.md", policy)


if __name__ == "__main__":
    unittest.main()
