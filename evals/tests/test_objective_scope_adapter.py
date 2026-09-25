import importlib.util
import json
from pathlib import Path
import unittest
import os
import sys
import tempfile

from evals import persistence


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "objective_scope_subject", ROOT / "evals/remaining-audit-behavior/codex_subject.py"
)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


class PromptIsolationTests(unittest.TestCase):
    def test_explicit_capture_limit_is_enforced_without_changing_other_campaigns(self):
        original = dict(persistence.LIMITS)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status, _, _ = persistence.bounded_process(
                [sys.executable, "-c", "print('x' * 200)"],
                cwd=root,
                env=os.environ.copy(),
                prompt="",
                raw=root,
                limits={"seconds": 5, "output_bytes": 100},
            )
            self.assertEqual(status, "output-limit")
            self.assertEqual((root / "codex.jsonl").stat().st_size, 100)
        self.assertEqual(persistence.LIMITS, original)

    def test_permission_labels_do_not_hide_controller_content(self):
        output = ROOT / "evals/artifacts/example/raw"
        home = output / "subject/codex-home"
        workspace = output.parent / "consumer"
        paths = dict(
            workspace=workspace,
            home=home,
            output_root=output,
            scratch=output / "subject/scratch",
            launcher_tmp=output / "subject/launcher-tmp",
        )
        metadata = json.dumps(
            [
                str(output.parent),
                str(output),
                str(home),
                str(paths["scratch"]),
                str(paths["launcher_tmp"]),
                str(home / "tmp/arg0/codex-arg0ABC"),
                f"(file: {workspace}/.agents/skills/to-spec/SKILL.md)",
            ]
        )
        subject.check_prompt_context(metadata, **paths)
        aliased = f"- `r0` = `{workspace}/.agents/skills`\n(file: r0/to-spec/SKILL.md)"
        subject.check_prompt_context(aliased, **paths)
        for invalid in (
            "(file: r9/to-spec/SKILL.md)",
            aliased + " (file: r0/../../../../rubric.md)",
            "- `r0` = `/unrelated/skills`\n(file: r0/to-spec/SKILL.md)",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                subject.check_prompt_context(invalid, **paths)
        for leak in (
            str(ROOT / "AGENTS.md"),
            str(output.parent / "rubric.md"),
            "source-repository instructions",
            "prior_conversation",
            "<memory",
            "(file: /unrelated/skill/SKILL.md)",
        ):
            with self.subTest(leak=leak), self.assertRaises(ValueError):
                subject.check_prompt_context(metadata + " " + leak, **paths)


if __name__ == "__main__":
    unittest.main()
