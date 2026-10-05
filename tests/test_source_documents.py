from __future__ import annotations

from pathlib import Path
import re
import unittest
import warnings

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPOSITORY_ROOT / "agent_workflow"
MANAGED_END = "<!-- agent-workflow:managed-end -->"

# Soft budgets: exceeding one warns rather than fails, prompting a deliberate review of what the
# always-loaded policy should hold.
DISTRIBUTED_POLICY_WORD_CEILING = 1500
SOURCE_POLICY_WORD_CEILING = 1250

# Authored current documents; fixtures, frozen reports, and effort state are excluded.
PROSE_ROOTS = (
    REPOSITORY_ROOT / "README.md",
    REPOSITORY_ROOT / "AGENTS.md",
    REPOSITORY_ROOT / "docs",
    REPOSITORY_ROOT / "architecture-decisions",
    REPOSITORY_ROOT / "tests/README.md",
    REPOSITORY_ROOT / ".devcontainer/README.md",
    REPOSITORY_ROOT / "evals/README.md",
    *sorted((REPOSITORY_ROOT / "evals").glob("*/README.md")),
    REPOSITORY_ROOT / ".agent-workflow",
    REPOSITORY_ROOT / ".agents/skills",
)
FROZEN_DOCUMENTS = (REPOSITORY_ROOT / "docs/audit-reconciliation",)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
SKIPPED_LINE = re.compile(r"^\s*(?:#|\||>)")
COMMENT_START = re.compile(r"^\s*<!--")
INDENTED_CODE = re.compile(r"^(?: {4}|\t)")
LINE_PREFIX = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?(?:\*\*\d+\.)?")
INLINE_CODE = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)")
LINK_DESTINATION = re.compile(r"\]\([^)]*\)")
QUOTED = re.compile(r"“[^”]*”|\"[^\"]*\"")
ABBREVIATION = re.compile(r"\b(?:e\.g|i\.e|etc|vs|No)\.")
SENTENCE_BOUNDARY = re.compile(r"[a-z0-9)\]*_][.!?]['’)\]*_]*\s+[A-Z\[*]")


def words(text: str) -> int:
    return len(text.split())


def multi_sentence_lines(text: str) -> list[int]:
    """Return 1-based prose lines that obviously hold more than one sentence."""
    flagged: list[int] = []
    lines = text.splitlines()
    start = 0
    if lines and lines[0] == "---" and "---" in lines[1:]:
        start = lines.index("---", 1) + 1
    fence = ""
    in_comment = False
    # Indented code cannot interrupt a paragraph, so an indented line continuing prose is still checked.
    in_paragraph = False
    for number, line in enumerate(lines[start:], start + 1):
        if in_comment:
            in_comment = "-->" not in line
            continue
        match = FENCE.match(line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence):
                fence = ""
            continue
        if match:
            fence = match[1]
            in_paragraph = False
            continue
        if not line.strip():
            in_paragraph = False
            continue
        if not in_paragraph and INDENTED_CODE.match(line):
            continue
        comment = COMMENT_START.match(line)
        if comment:
            in_comment = "-->" not in line[comment.end() :]
            in_paragraph = False
            continue
        if SKIPPED_LINE.match(line):
            in_paragraph = False
            continue
        in_paragraph = True
        prose = LINE_PREFIX.sub("", line)
        prose = INLINE_CODE.sub("code", prose)
        prose = LINK_DESTINATION.sub("]", prose)
        prose = ABBREVIATION.sub("abbr", QUOTED.sub("quote", prose))
        if SENTENCE_BOUNDARY.search(prose):
            flagged.append(number)
    return flagged


def prose_documents() -> list[Path]:
    paths: list[Path] = []
    for root in PROSE_ROOTS:
        if root.is_file():
            paths.append(root)
        elif root.is_dir():
            paths.extend(sorted(root.rglob("*.md")))
    return [
        path
        for path in paths
        if not any(path.is_relative_to(frozen) for frozen in FROZEN_DOCUMENTS)
    ]


class SourceDocumentTests(unittest.TestCase):
    """Flag always-loaded policy size and guard the mechanical part of the Markdown line-break policy."""

    def test_always_loaded_policy_warns_past_word_budgets(self) -> None:
        distributed = (PACKAGE_ROOT / "install/AGENTS.md.template").read_text(
            encoding="utf-8"
        )
        source = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        source_only = source.split(MANAGED_END, 1)[1]
        for label, text, ceiling in (
            ("distributed root policy", distributed, DISTRIBUTED_POLICY_WORD_CEILING),
            ("source-only root policy", source_only, SOURCE_POLICY_WORD_CEILING),
        ):
            count = words(text)
            if count > ceiling:
                warnings.warn(
                    f"{label} has {count} words, past its {ceiling}-word soft budget; "
                    "consider removing or consolidating instructions",
                    stacklevel=1,
                )

    def test_prose_lines_hold_one_sentence(self) -> None:
        violations = [
            f"{path.relative_to(REPOSITORY_ROOT)}:{number}"
            for path in prose_documents()
            for number in multi_sentence_lines(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(violations, [], "put each sentence on its own line")

    def test_sentence_check_rejects_collapsed_sentences(self) -> None:
        for text in (
            "First sentence. Second sentence.",
            "- A list item. Another sentence.",
            "Ends with code `x`. Then [a link](y.md) follows.",
            "Question? Answer.",
            "``code`` ends. Next sentence.",
        ):
            with self.subTest(text=text):
                self.assertEqual(multi_sentence_lines(text), [1])

    def test_sentence_check_resumes_after_skipped_blocks(self) -> None:
        for text, expected in (
            ("Paragraph line\n    continues here. Next sentence.", [2]),
            ("    code = 1. Code = 2\n\nAfter one. After two.", [3]),
            ("<!-- note -->\nAfter one. After two.", [2]),
            ("<!--\nhidden\n-->\nAfter one. After two.", [4]),
        ):
            with self.subTest(text=text):
                self.assertEqual(multi_sentence_lines(text), expected)

    def test_sentence_check_accepts_legitimate_lines(self) -> None:
        for text in (
            "One sentence per line.\nAnother sentence.",
            "1. **Objective** — the result.",
            "**1. Use dependency injection**",
            "Use a flag, e.g. Verbose mode, when needed.",
            "Run `make test. Then` inside code.",
            "See [the guide](docs/a.md. B) for detail.",
            "The prompt said “Stop. Wait.” before continuing.",
            "| Cell one. | Cell Two. |",
            "```text\nFirst. Second.\n```",
            "---\ndescription: One. Two.\n---\nBody.",
            "> Quoted one. Quoted two.",
            "Intro sentence.\n\n    first = 1. Second = 2",
            "- Item.\n\n        nested = 1. Code = 2",
            "<!--\nHidden one. Hidden two.\n-->",
            "Use ``a `b`. C`` here.",
        ):
            with self.subTest(text=text):
                self.assertEqual(multi_sentence_lines(text), [])


if __name__ == "__main__":
    unittest.main()
