"""Structural guards for canonical repository-read skill references.

These checks cover paths and distribution, not instruction meaning or live host
behavior. Review covers the prose; the opt-in Claude protocol covers compliance.
"""

from __future__ import annotations

import json
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

    def test_curated_skills_keep_one_canonical_distribution_tree(self):
        manifest = json.loads(
            (ROOT / "agent_workflow/install/manifest.json").read_text(encoding="utf-8")
        )
        skill_entries = [
            entry
            for entry in manifest["framework_owned"]
            if entry["source"].startswith(".agents/skills/")
        ]
        self.assertTrue(skill_entries)
        for entry in skill_entries:
            with self.subTest(source=entry["source"]):
                self.assertEqual(entry["source"], entry["target"])
        self.assertFalse(
            any(
                entry["target"].startswith(".claude/skills/")
                for entry in manifest["framework_owned"]
            )
        )


if __name__ == "__main__":
    unittest.main()
