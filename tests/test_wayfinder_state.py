"""Contract/fixture checks, not a Wayfinder selector or mutation implementation.

Agent safety and semantic behavior still require opt-in execution evidence.
See tests/README.md for the retained boundaries and explicitly unverified requirements.
"""

from pathlib import Path
import re
import shutil
import tempfile
import unittest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPOSITORY_ROOT / "agent_workflow"
CONTRACT = REPOSITORY_ROOT / ".agent-workflow/contracts/wayfinder-state.md"
FIXTURES = REPOSITORY_ROOT / "tests/fixtures"


def identifier_errors(effort: Path) -> list[str]:
    """Check only literal IDs in an explicitly selected fixture; never select or mutate."""
    errors = []
    for kind, container in (
        ("F", "facts.md"),
        ("D", "decisions.md"),
        ("U", "unknowns.md"),
        ("E", "evidence"),
    ):
        path = effort / container
        if path.is_symlink():
            errors.append(f"symlink: {container}")
            continue
        if kind in "UFD":
            candidates = (
                [
                    line
                    for line in path.read_text().splitlines()
                    if re.match(rf"## {kind}(?:[0-9]|\b)", line)
                ]
                if path.is_file()
                else []
            )
            pattern = rf"## {kind}([1-9][0-9]*) — \S.*"
        else:
            candidates = (
                [item.name for item in path.iterdir() if item.name.startswith(kind)]
                if path.is_dir()
                else []
            )
            pattern = rf"{kind}([1-9][0-9]*)-[^.]+\.md"
        seen = set()
        for candidate in candidates:
            match = re.fullmatch(pattern, candidate)
            if match is None:
                errors.append(f"malformed {kind}: {candidate}")
            elif match[1] in seen:
                errors.append(f"duplicate {kind}{match[1]}")
            else:
                seen.add(match[1])
            if kind == "E" and (
                (path / candidate).is_symlink() or not (path / candidate).is_file()
            ):
                errors.append(f"unsafe record: {candidate}")
    return errors


def broken_fixture_links(paths: list[Path]) -> list[str]:
    """Check Markdown links in the named files, without discovering more state."""
    broken = []
    for path in paths:
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
            filename, _, anchor = target.partition("#")
            destination = path.parent / filename if filename else path
            if destination.is_symlink() or not destination.is_file():
                broken.append(target)
            elif anchor:
                headings = re.findall(
                    r"^## (.+)$", destination.read_text(), re.MULTILINE
                )
                anchors = [
                    re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                    for heading in headings
                ]
                if anchor not in anchors:
                    broken.append(target)
    return broken


class WayfinderStateContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = CONTRACT.read_text()

    def test_settlement_fixtures_keep_identifiers_support_and_project_bytes(self):
        before = (
            FIXTURES
            / "wayfinder-reference-settlement/.project-efforts/release-direction"
        )
        after = (
            FIXTURES
            / "wayfinder-reference-settlement-after/.project-efforts/release-direction"
        )
        for effort in (before, after):
            self.assertEqual(identifier_errors(effort), [])
            self.assertEqual(
                broken_fixture_links(
                    [effort / name for name in ("map.md", "facts.md", "decisions.md")]
                ),
                [],
            )
        self.assertEqual(
            (before / "project-notes.txt").read_bytes(),
            (after / "project-notes.txt").read_bytes(),
        )
        self.assertIn(
            "## F8 — Published source selects staged release",
            (after / "facts.md").read_text(),
        )
        self.assertIn(
            "## D4 — Adopt the staged release direction",
            (after / "decisions.md").read_text(),
        )
        self.assertIn("../../source.txt", (after / "facts.md").read_text())
        for name in ("map.md", "facts.md", "decisions.md"):
            text = (after / name).read_text()
            self.assertNotRegex(text, r"\b(?:U17|E12)\b")
        self.assertFalse((after / "unknowns.md").exists())
        self.assertFalse((after / "evidence/E12-source-observation.md").exists())

    def test_identifier_checks_reject_duplicate_malformed_zero_and_symlink_records(
        self,
    ):
        source = (
            FIXTURES
            / "wayfinder-reference-settlement/.project-efforts/release-direction"
        )
        for relative, content, expected in (
            ("facts.md", "# Facts\n\n## F8 — A\n\n## F8 — B\n", "duplicate F8"),
            ("decisions.md", "# Decisions\n\n## D0 — Bad\n", "malformed D"),
            ("unknowns.md", "## U17 — A\n\n## U17 — B\n", "duplicate U17"),
            ("unknowns.md", "## U0 — Bad\n", "malformed U"),
            ("evidence/E0-zero.md", "zero", "malformed E"),
        ):
            with (
                self.subTest(relative=relative),
                tempfile.TemporaryDirectory() as temporary,
            ):
                effort = Path(temporary) / "effort"
                shutil.copytree(source, effort)
                (effort / relative).write_text(content)
                self.assertTrue(
                    any(expected in error for error in identifier_errors(effort))
                )
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            shutil.copytree(source, effort)
            (effort / "unknowns.md").unlink()
            (effort / "unknowns.md").symlink_to(effort / "project-notes.txt")
            self.assertIn("symlink: unknowns.md", identifier_errors(effort))

    def test_unrecognized_ledger_heading_is_not_a_malformed_identifier(self):
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary)
            (effort / "unknowns.md").write_text(
                "## U1 — A question?\n\n## Unrelated notes\nProject-owned bytes.\n"
            )
            self.assertEqual(identifier_errors(effort), [])

    def test_link_checks_reject_dangling_file_and_renamed_ledger_anchor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            current = root / "map.md"
            facts = root / "facts.md"
            facts.write_text("# Facts\n\n## F8 — Renamed title\n")
            current.write_text(
                "[Fact](facts.md#f8--old-title)\n[Question](unknowns/U17-missing.md)\n"
            )
            self.assertEqual(
                broken_fixture_links([current]),
                ["facts.md#f8--old-title", "unknowns/U17-missing.md"],
            )
            current.write_text("[Fact](facts.md#f8--renamed-title)\n")
            self.assertEqual(broken_fixture_links([current]), [])

    def test_contract_documents_state_paths(self) -> None:
        for path in (
            ".project-efforts/<effort>/map.md",
            "facts.md",
            "decisions.md",
            "unknowns.md",
            "evidence/E<ID>-<slug>.md",
        ):
            with self.subTest(path=path):
                self.assertIn(path, self.contract)

    def test_contract_documents_record_type_inventory(self) -> None:
        self.assertEqual(
            set(re.findall(r"^- `([A-Z])#`", self.contract, re.MULTILINE)),
            {"U", "E", "F", "D"},
        )

    def test_contract_documents_evidence_and_authority_fields(self) -> None:
        for field in (
            "`Source:`",
            "`Scope:`",
            "`Authority:`",
            "`Derived from:`",
            "`Limitations:`",
            "`Observation`",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.contract)

    def test_contract_keeps_identifier_and_anchor_representation(self) -> None:
        for representation in (
            "## U<ID> — <question>",
            "## F<ID> — <title>",
            "## D<ID> — <title>",
            "u<ID>--<slug>",
            "f<ID>--<slug>",
            "d<ID>--<slug>",
        ):
            with self.subTest(representation=representation):
                self.assertIn(representation, self.contract)

    def test_composite_policy_matches_install_template(self) -> None:
        source_policy = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        managed = source_policy.split("<!-- agent-workflow:managed-begin -->", 1)[1]
        managed = managed.split("<!-- agent-workflow:managed-end -->", 1)[0].strip()
        packaged_policy = (
            (PACKAGE_ROOT / "install/AGENTS.md.template")
            .read_text(encoding="utf-8")
            .strip()
        )
        self.assertEqual(packaged_policy, managed)


if __name__ == "__main__":
    unittest.main()
