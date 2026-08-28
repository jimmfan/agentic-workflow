from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import re
import shutil
import tempfile
import threading
import time
from typing import Callable
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
CONTRACT = PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
INSTALLED_CONTRACT = REPOSITORY_ROOT / ".agent-workflow/contracts/wayfinder-state.md"
RUNTIME = PACKAGE_ROOT / "runtime-projections/wayfinder.md"
GENERATED_SKILL = REPOSITORY_ROOT / ".agents/skills/wayfinder/SKILL.md"
FIXTURES = PACKAGE_ROOT / "tests/fixtures"
TYPE_DIRECTORIES = {"U": "unknowns", "E": "evidence", "F": "facts", "D": "decisions"}
LEDGER_PATHS = {"F": "facts.md", "D": "decisions.md"}
LEDGER_TITLES = {"F": "Facts", "D": "Decisions"}
CURRENT_ID = re.compile(r"^([UEFD])([1-9][0-9]*)-([^.]+)\.md$")
LEDGER_HEADING = re.compile(r"^## ([FD])([1-9][0-9]*) — (\S.*)$")


class UnsafeWayfinderState(RuntimeError):
    pass


def validate_effort(effort: Path) -> bool:
    map_path = effort / "map.md"
    if map_path.is_symlink() or not map_path.is_file():
        raise UnsafeWayfinderState("effort has no safe map")
    return True


def ledger_sections(effort: Path, kind: str) -> list[tuple[int, str, str]]:
    path = effort / LEDGER_PATHS[kind]
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise UnsafeWayfinderState(f"unsafe {kind} ledger")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    starts: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        match = LEDGER_HEADING.fullmatch(line.rstrip("\r\n"))
        if match is None or match.group(1) != kind:
            raise UnsafeWayfinderState(f"malformed current {kind} identifier")
        starts.append((index, int(match.group(2)), match.group(3)))
    identifiers = [identifier for _, identifier, _ in starts]
    if len(identifiers) != len(set(identifiers)):
        raise UnsafeWayfinderState(f"duplicate current {kind} identifier")
    sections: list[tuple[int, str, str]] = []
    for position, (start, identifier, title) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        sections.append((identifier, title, "".join(lines[start:end])))
    return sections


def read_current_ids(effort: Path, kind: str) -> list[int]:
    if kind in LEDGER_PATHS:
        return [item[0] for item in ledger_sections(effort, kind)]
    return sorted(current_ids(effort, kind))


def readable_slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def create_current_record(
    effort: Path,
    kind: str,
    title: str,
    body: str,
    *,
    before_lock: Callable[[], None] | None = None,
    before_final_write: Callable[[], None] | None = None,
    lock_attempts: int = 1_000,
) -> str:
    if kind not in TYPE_DIRECTORIES:
        raise UnsafeWayfinderState("unknown Wayfinder record type")
    if kind in ("U", "E"):
        path = create_current_child(
            effort,
            kind,
            readable_slug(title),
            body,
            before_lock=before_lock,
            lock_attempts=lock_attempts,
        )
        return path.name.split("-", 1)[0]
    if before_lock is not None:
        before_lock()
    with effort_mutation_lock(effort, attempts=lock_attempts):
        path = effort / LEDGER_PATHS[kind]
        sections = ledger_sections(effort, kind)
        identifier = max((item[0] for item in sections), default=0) + 1
        observed = path.read_bytes() if path.exists() else None
        existing = observed.decode("utf-8") if observed is not None else ""
        if before_final_write is not None:
            before_final_write()
        current = path.read_bytes() if path.exists() else None
        if current != observed:
            raise UnsafeWayfinderState("ledger changed before write")
        prefix = existing.rstrip() if existing else f"# {LEDGER_TITLES[kind]}"
        content = (
            f"{prefix}\n\n## {kind}{identifier} — {title}\n\n"
            f"{body.rstrip()}\n"
        )
        path.write_text(content, encoding="utf-8")
        return f"{kind}{identifier}"


def heading_anchor(kind: str, identifier: int, title: str) -> str:
    heading = f"{kind}{identifier} — {title}".lower()
    without_punctuation = "".join(
        character
        for character in heading
        if character.isalnum() or character in {" ", "-"}
    )
    return without_punctuation.replace(" ", "-")


def ledger_references(
    effort: Path,
    kind: str,
    identifier: int,
    title: str,
    ledger_without_target: str,
    known_references: list[Path] | None = None,
) -> list[Path]:
    token = re.compile(rf"(?<![A-Z0-9]){kind}{identifier}(?![0-9])")
    ledger_name = LEDGER_PATHS[kind]
    anchor = heading_anchor(kind, identifier, title)
    references: list[Path] = []
    paths = list(current_markdown(effort))
    paths.extend(known_references or [])
    for path in dict.fromkeys(paths):
        if path.is_symlink() or not path.is_file():
            raise UnsafeWayfinderState(f"unsafe reference path: {path}")
        text = (
            ledger_without_target
            if path == effort / ledger_name
            else path.read_text(encoding="utf-8")
        )
        if token.search(text) or f"{ledger_name}#{anchor}" in text:
            references.append(path)
    return references


def retire_ledger_section(
    effort: Path,
    kind: str,
    identifier: int,
    *,
    known_references: list[Path] | None = None,
    before_final_check: Callable[[], None] | None = None,
    lock_attempts: int = 1_000,
) -> bool:
    path = effort / LEDGER_PATHS[kind]
    with effort_mutation_lock(effort, attempts=lock_attempts):
        if not path.exists():
            return False
        original = path.read_text(encoding="utf-8")
        sections = ledger_sections(effort, kind)
        matches = [item for item in sections if item[0] == identifier]
        if not matches:
            return False
        _, title, section = matches[0]
        updated = original.replace(section, "", 1)
        if ledger_references(
            effort,
            kind,
            identifier,
            title,
            updated,
            known_references,
        ):
            raise UnsafeWayfinderState("current references remain")
        observed_current = current_markdown(effort)
        observed_known = {
            reference: reference.read_bytes()
            for reference in known_references or []
            if not reference.is_relative_to(effort)
        }
        if before_final_check is not None:
            before_final_check()
        if current_markdown(effort) != observed_current:
            raise UnsafeWayfinderState("current state changed during reconciliation")
        if any(
            not reference.is_file() or reference.read_bytes() != observed
            for reference, observed in observed_known.items()
        ):
            raise UnsafeWayfinderState("known reference changed during reconciliation")
        if ledger_references(
            effort,
            kind,
            identifier,
            title,
            updated,
            known_references,
        ):
            raise UnsafeWayfinderState("current references appeared during reconciliation")
        if len(sections) == 1:
            path.unlink()
        else:
            path.write_text(updated, encoding="utf-8")
        return True


def replace_map(
    effort: Path,
    expected: bytes,
    updated: bytes,
    *,
    lock_attempts: int = 1_000,
) -> None:
    with effort_mutation_lock(effort, attempts=lock_attempts):
        path = effort / "map.md"
        if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
            raise UnsafeWayfinderState("map changed before write")
        path.write_bytes(updated)


def current_child_paths(effort: Path, kind: str) -> list[Path]:
    directory = effort / TYPE_DIRECTORIES[kind]
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise UnsafeWayfinderState(f"unsafe {kind} directory")

    result: list[Path] = []
    identifiers: list[int] = []
    for child in directory.iterdir():
        if child.is_symlink() or not child.is_file():
            raise UnsafeWayfinderState(f"unsafe child path: {child.name}")
        match = CURRENT_ID.fullmatch(child.name)
        if match is None or match.group(1) != kind:
            raise UnsafeWayfinderState(f"unrecognized child filename: {child.name}")
        result.append(child)
        identifiers.append(int(match.group(2)))
    if len(identifiers) != len(set(identifiers)):
        raise UnsafeWayfinderState(f"duplicate current {kind} identifier")
    return sorted(result)


def current_ids(effort: Path, kind: str) -> list[int]:
    return [
        int(CURRENT_ID.fullmatch(path.name).group(2))
        for path in current_child_paths(effort, kind)
    ]


def next_current_id(effort: Path, kind: str) -> int:
    ids = current_ids(effort, kind)
    return max(ids, default=0) + 1


@contextmanager
def effort_mutation_lock(effort: Path, *, attempts: int = 1_000):
    effort.mkdir(parents=True, exist_ok=True)
    lock = effort / ".wayfinder-mutation-lock"
    for _ in range(attempts):
        try:
            lock.mkdir()
        except FileExistsError:
            time.sleep(0.001)
            continue
        break
    else:
        raise UnsafeWayfinderState("effort mutation lock is unavailable")
    try:
        yield
    finally:
        lock.rmdir()


def create_current_child(
    effort: Path,
    kind: str,
    slug: str,
    body: str,
    before_lock: Callable[[], None] | None = None,
    lock_attempts: int = 1_000,
) -> Path:
    if kind not in {"U", "E"}:
        raise UnsafeWayfinderState("F/D records belong in their current ledgers")
    if before_lock is not None:
        before_lock()
    with effort_mutation_lock(effort, attempts=lock_attempts):
        directory = effort / TYPE_DIRECTORIES[kind]
        directory.mkdir(parents=True, exist_ok=True)
        candidate = next_current_id(effort, kind)
        path = directory / f"{kind}{candidate}-{slug}.md"
        with path.open("x", encoding="utf-8") as handle:
            handle.write(body)
        return path


def current_markdown(
    effort: Path, *, excluding: Path | None = None
) -> dict[Path, bytes]:
    result: dict[Path, bytes] = {}
    paths = [effort / "map.md", effort / "facts.md", effort / "decisions.md"]
    paths.extend(current_child_paths(effort, "U"))
    paths.extend(current_child_paths(effort, "E"))
    for path in paths:
        if path == excluding:
            continue
        if not path.exists() and not path.is_symlink():
            continue
        if path.is_symlink() or not path.is_file():
            raise UnsafeWayfinderState(f"unsafe reference path: {path}")
        result[path] = path.read_bytes()
    return result


def references_to(effort: Path, target: Path) -> list[Path]:
    match = CURRENT_ID.fullmatch(target.name)
    if match is None:
        raise UnsafeWayfinderState("retiring path has no canonical current ID")
    identifier = f"{match.group(1)}{match.group(2)}"
    token = re.compile(rf"(?<![A-Z0-9]){re.escape(identifier)}(?![0-9])")
    relative_path = target.relative_to(effort).as_posix()
    references: list[Path] = []
    for path, content in current_markdown(effort, excluding=target).items():
        text = content.decode("utf-8")
        if token.search(text) or target.name in text or relative_path in text:
            references.append(path)
    return references


def retire_current_child(
    effort: Path,
    target: Path,
    *,
    before_final_check: Callable[[], None] | None = None,
    lock_attempts: int = 1_000,
) -> bool:
    match = CURRENT_ID.fullmatch(target.name)
    if match is not None and match.group(1) in LEDGER_PATHS:
        raise UnsafeWayfinderState("F/D records belong in their current ledgers")
    with effort_mutation_lock(effort, attempts=lock_attempts):
        if not target.exists():
            return False
        references = references_to(effort, target)
        if references:
            raise UnsafeWayfinderState(f"current references remain: {references}")

        observed_target = target.read_bytes()
        observed_current = current_markdown(effort, excluding=target)
        if before_final_check is not None:
            before_final_check()
        if not target.exists() or target.read_bytes() != observed_target:
            raise UnsafeWayfinderState("retiring child changed during reconciliation")
        if current_markdown(effort, excluding=target) != observed_current:
            raise UnsafeWayfinderState("current state changed during reconciliation")
        if references_to(effort, target):
            raise UnsafeWayfinderState(
                "current references appeared during reconciliation"
            )

        target.unlink()
        parent = target.parent
        if not any(parent.iterdir()):
            parent.rmdir()
        return True


class WayfinderStateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = CONTRACT.read_text(encoding="utf-8")
        self.normalized = " ".join(self.contract.split())

    def test_new_effort_can_remain_map_only_or_create_a_fact_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Map only\n", encoding="utf-8")

            self.assertTrue(validate_effort(effort))
            self.assertEqual(list(effort.iterdir()), [effort / "map.md"])

            created = create_current_record(
                effort,
                "F",
                "The map can stand alone",
                "- Status: established\n"
                "- Source: README.md\n\n"
                "A map-only effort is valid.\n",
            )

            self.assertEqual(created, "F1")
            self.assertEqual(
                (effort / "facts.md").read_text(encoding="utf-8"),
                "# Facts\n\n"
                "## F1 — The map can stand alone\n\n"
                "- Status: established\n"
                "- Source: README.md\n\n"
                "A map-only effort is valid.\n",
            )

    def test_decision_ledger_allocates_after_the_highest_valid_unique_heading(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Decisions\n", encoding="utf-8")
            ledger = effort / "decisions.md"
            ledger.write_text(
                "# Decisions\n\n"
                "## D1 — First choice\n\n- Status: accepted\n\nFirst.\n\n"
                "## D3 — Third choice\n\n- Status: accepted\n\nThird.\n",
                encoding="utf-8",
            )

            created = create_current_record(
                effort,
                "D",
                "Fourth choice",
                "- Status: provisional\n"
                "- Authority: User, 2026-08-25, request\n"
                "- Revisit when: Tests disagree\n\nFourth.\n",
            )
            self.assertEqual(created, "D4")
            self.assertIn("## D4 — Fourth choice", ledger.read_text(encoding="utf-8"))

            ledger.write_text(
                ledger.read_text(encoding="utf-8")
                + "\n## D4 — Duplicate\n\nDuplicate.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(UnsafeWayfinderState, "duplicate current D"):
                create_current_record(effort, "D", "Blocked", "Blocked.\n")

            ledger.write_text(
                "# Decisions\n\n## D0 — Malformed\n\nMalformed.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(UnsafeWayfinderState, "malformed current D"):
                create_current_record(effort, "D", "Blocked", "Blocked.\n")

    def test_unrecognized_project_content_is_not_interpreted_as_current_references(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            unknown = effort / "unrecognized-project-data/note.md"
            unknown.parent.mkdir(parents=True)
            unknown.write_bytes(
                b"Project-owned prose that happens to mention F1.\n"
            )
            (effort / "map.md").write_text("# Independent retirement\n", encoding="utf-8")
            ledger = effort / "facts.md"
            ledger.write_text(
                "# Facts\n\n## F1 — Current fact\n\n"
                "- Source: source.md\n\nCurrent.\n",
                encoding="utf-8",
            )

            self.assertTrue(retire_ledger_section(effort, "F", 1))
            self.assertFalse(ledger.exists())
            self.assertEqual(
                unknown.read_bytes(),
                b"Project-owned prose that happens to mention F1.\n",
            )

    def test_ledger_retirement_removes_only_the_reconciled_section_and_empty_ledger(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            effort = project / ".agent-wayfinder/effort"
            effort.mkdir(parents=True)
            docs = project / "docs"
            docs.mkdir()
            external = docs / "current.md"
            map_path = effort / "map.md"
            map_path.write_text(
                "# Retirement\n\n"
                "Read [the first fact](facts.md#f1--first-fact).\n",
                encoding="utf-8",
            )
            external.write_text(
                "[First fact](../.agent-wayfinder/effort/facts.md#f1--first-fact)\n",
                encoding="utf-8",
            )
            ledger = effort / "facts.md"
            remaining_section = (
                "## F3 — Remaining fact\n\n"
                "- Source: source.md\n\nRemaining.\n"
            )
            ledger.write_text(
                "# Facts\n\n"
                "## F1 — First fact\n\n- Source: source.md\n\nFirst.\n\n"
                + remaining_section,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                retire_ledger_section(effort, "F", 1, known_references=[external])

            map_path.write_text("# Retirement\n\nOnly F3 remains.\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                retire_ledger_section(effort, "F", 1, known_references=[external])
            external.write_text("The first fact was reconciled.\n", encoding="utf-8")
            self.assertTrue(
                retire_ledger_section(effort, "F", 1, known_references=[external])
            )
            remaining = ledger.read_text(encoding="utf-8")
            self.assertEqual(remaining, "# Facts\n\n" + remaining_section)

            map_path.write_text("# Retirement\n\nNo ledger facts remain.\n", encoding="utf-8")
            self.assertTrue(retire_ledger_section(effort, "F", 3))
            self.assertFalse(ledger.exists())
            self.assertFalse(retire_ledger_section(effort, "F", 3))

    def test_ledger_append_rereads_before_write_and_preserves_a_concurrent_claim(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Concurrent append\n", encoding="utf-8")
            ledger = effort / "facts.md"
            ledger.write_text(
                "# Facts\n\n## F1 — First\n\n- Source: source.md\n\nFirst.\n",
                encoding="utf-8",
            )

            def concurrent_claim() -> None:
                ledger.write_text(
                    ledger.read_text(encoding="utf-8").rstrip()
                    + "\n\n## F2 — Concurrent\n\n- Source: source.md\n\nConcurrent.\n",
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(UnsafeWayfinderState, "ledger changed"):
                create_current_record(
                    effort,
                    "F",
                    "Would overwrite",
                    "- Source: source.md\n\nUnsafe.\n",
                    before_final_write=concurrent_claim,
                )

            self.assertEqual(read_current_ids(effort, "F"), [1, 2])
            self.assertNotIn("Would overwrite", ledger.read_text(encoding="utf-8"))

    def test_one_effort_lock_covers_map_ledgers_unknowns_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            map_path = effort / "map.md"
            map_path.write_text("# Locked effort\n", encoding="utf-8")
            self.assertEqual(
                create_current_record(effort, "U", "Independent question", "Question.\n"),
                "U1",
            )
            self.assertEqual(
                create_current_record(effort, "E", "Substantial evidence", "Evidence.\n"),
                "E1",
            )
            self.assertTrue((effort / "unknowns/U1-independent-question.md").is_file())
            self.assertTrue((effort / "evidence/E1-substantial-evidence.md").is_file())
            self.assertFalse((effort / "unknowns.md").exists())
            self.assertFalse((effort / "evidence.md").exists())

            lock = effort / ".wayfinder-mutation-lock"
            lock.mkdir()
            try:
                with self.assertRaisesRegex(UnsafeWayfinderState, "effort mutation lock"):
                    replace_map(
                        effort,
                        b"# Locked effort\n",
                        b"# Changed\n",
                        lock_attempts=1,
                    )
                for kind in ("U", "E", "F", "D"):
                    with self.subTest(kind=kind):
                        with self.assertRaisesRegex(
                            UnsafeWayfinderState, "effort mutation lock"
                        ):
                            create_current_record(
                                effort,
                                kind,
                                "Blocked",
                                "Blocked.\n",
                                lock_attempts=1,
                            )
            finally:
                lock.rmdir()

            self.assertEqual(map_path.read_bytes(), b"# Locked effort\n")

    def test_current_state_allocation_skips_gaps_and_may_reuse_retired_highest(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Allocation\n", encoding="utf-8")

            first = create_current_record(effort, "D", "First", "First.\n")
            second = create_current_record(effort, "D", "Second", "Second.\n")
            third = create_current_record(effort, "D", "Third", "Third.\n")
            preserved = {
                identifier: section
                for identifier, _, section in ledger_sections(effort, "D")
                if identifier in {1, 3}
            }

            self.assertEqual(
                (first, second, third),
                ("D1", "D2", "D3"),
            )
            self.assertTrue(retire_ledger_section(effort, "D", 2))
            fourth = create_current_record(effort, "D", "Fourth", "Fourth.\n")
            self.assertEqual(fourth, "D4")

            self.assertTrue(retire_ledger_section(effort, "D", 4))
            replacement = create_current_record(
                effort, "D", "Replacement", "New meaning.\n"
            )

            self.assertEqual(replacement, "D4")
            current = {
                identifier: section
                for identifier, _, section in ledger_sections(effort, "D")
            }
            self.assertEqual(current[1].rstrip(), preserved[1].rstrip())
            self.assertEqual(current[3].rstrip(), preserved[3].rstrip())
            self.assertTrue((effort / "decisions.md").is_file())

    def test_atomic_effort_lock_serializes_simultaneous_decision_allocations(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Concurrent allocation\n", encoding="utf-8")
            barrier = threading.Barrier(2)
            created: list[str] = []
            errors: list[BaseException] = []

            def create(slug: str) -> None:
                try:
                    created.append(
                        create_current_record(
                            effort,
                            "D",
                            slug.title(),
                            f"{slug.title()}.\n",
                            before_lock=barrier.wait,
                        )
                    )
                except BaseException as error:  # captured for deterministic assertion
                    errors.append(error)

            threads = [
                threading.Thread(target=create, args=("alpha",)),
                threading.Thread(target=create, args=("beta",)),
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            self.assertEqual(errors, [])
            self.assertEqual(set(created), {"D1", "D2"})
            self.assertEqual(
                [identifier for identifier, _, _ in ledger_sections(effort, "D")],
                [1, 2],
            )
            self.assertTrue((effort / "decisions.md").is_file())
            self.assertFalse((effort / ".wayfinder-mutation-lock").exists())

    def test_answered_unknown_retirement_requires_reconciled_references_and_is_idempotent(
        self,
    ) -> None:
        fixture = FIXTURES / "wayfinder-reference-settlement"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            shutil.copytree(fixture, root)
            effort = root / ".agent-wayfinder/provider-state"
            unknown = effort / "unknowns/U17-provider-tracker-state.md"
            evidence = effort / "evidence/E12-provider-configuration.md"
            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                retire_current_child(effort, unknown)

            (effort / "map.md").write_text(
                "# Provider state settlement\n\n- Status: current\n\n"
                "## Current state\n\n[F8](facts.md#f8--provider-needs-no-tracker-state) and "
                "[D4](decisions.md#d4--use-the-local-runtime-without-tracker-state) "
                "remain current.\n",
                encoding="utf-8",
            )
            fact = effort / "facts.md"
            fact.write_text(
                fact.read_text(encoding="utf-8").replace(
                    "- Derived from: E12",
                    "- Source: [source.txt](../../source.txt)",
                ),
                encoding="utf-8",
            )
            decision = effort / "decisions.md"
            decision.write_text(
                decision.read_text(encoding="utf-8").replace(
                    "- Based on: U17, F8", "- Based on: F8"
                ),
                encoding="utf-8",
            )
            unknown.write_text(
                unknown.read_text(encoding="utf-8")
                .replace("Related: E12, F8, D4", "Related: F8, D4")
                .replace(
                    "E12 establishes that tracker state is not required.",
                    "The answer is recorded in current state.",
                ),
                encoding="utf-8",
            )
            evidence.write_text(
                evidence.read_text(encoding="utf-8").replace(
                    "Related: U17, F8", "Related: F8"
                ),
                encoding="utf-8",
            )
            self.assertTrue(retire_current_child(effort, evidence))
            self.assertTrue(retire_current_child(effort, unknown))
            self.assertFalse(retire_current_child(effort, evidence))
            source_link = (fact.parent / "../../source.txt").resolve()
            self.assertEqual(source_link, (root / "source.txt").resolve())
            self.assertTrue(source_link.is_file())
            self.assertNotIn("U17", decision.read_text(encoding="utf-8"))

    def test_uncommitted_child_can_retire_and_busy_lock_preserves_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            unknown = unknowns / "U1-transient.md"
            unknown.write_text("# U1: Transient question\n", encoding="utf-8")

            self.assertTrue(retire_current_child(effort, unknown))
            self.assertFalse(unknown.exists())

            unknowns.mkdir()
            replacement = unknowns / "U1-current.md"
            replacement.write_text("# U1: Current question\n", encoding="utf-8")
            (effort / ".wayfinder-mutation-lock").mkdir()
            with self.assertRaisesRegex(UnsafeWayfinderState, "effort mutation lock"):
                create_current_child(
                    effort, "U", "blocked", "blocked\n", lock_attempts=1
                )
            with self.assertRaisesRegex(UnsafeWayfinderState, "effort mutation lock"):
                retire_current_child(effort, replacement, lock_attempts=1)
            self.assertTrue(replacement.exists())
            self.assertTrue((effort / ".wayfinder-mutation-lock").is_dir())

    def test_answered_unknown_without_independent_outcome_can_settle_to_map_only(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "map-only"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            map_path = effort / "map.md"
            unknown = unknowns / "U1-tracker-state.md"
            map_path.write_text("# Map only\n\nU1 remains open.\n", encoding="utf-8")
            unknown.write_text("# U1: Tracker state?\n", encoding="utf-8")
            map_path.write_text(
                "# Map only\n\nTracker state is not required.\n",
                encoding="utf-8",
            )
            self.assertTrue(retire_current_child(effort, unknown))

            self.assertEqual(
                [path.relative_to(effort).as_posix() for path in effort.iterdir()],
                ["map.md"],
            )

    def test_empty_unknowns_directory_has_no_current_state_meaning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "empty-unknowns"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            map_path = effort / "map.md"
            map_path.write_text(
                "# Empty unknowns\n\nThe ready frontier has no blocker.\n",
                encoding="utf-8",
            )

            self.assertEqual(current_ids(effort, "U"), [])
            self.assertEqual(next_current_id(effort, "U"), 1)
            self.assertEqual(current_markdown(effort), {map_path: map_path.read_bytes()})
            self.assertTrue(unknowns.is_dir())

    def test_retirement_rechecks_current_state_under_effort_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            map_path = effort / "map.md"
            map_path.write_text("# Concurrent retirement\n", encoding="utf-8")
            unknown = unknowns / "U1-transient.md"
            unknown.write_text("# U1: Transient question\n", encoding="utf-8")

            def concurrent_reference() -> None:
                map_path.write_text(
                    map_path.read_text(encoding="utf-8") + "\nU1 is still needed.\n",
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current state changed"):
                retire_current_child(
                    effort, unknown, before_final_check=concurrent_reference
                )
            self.assertTrue(unknown.exists())
            self.assertFalse((effort / ".wayfinder-mutation-lock").exists())

    def test_unsafe_current_paths_block_allocation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            directory = effort / "unknowns"
            directory.mkdir(parents=True)
            (directory / "notes.md").write_text(
                "not a canonical child\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                UnsafeWayfinderState, "unrecognized child filename"
            ):
                next_current_id(effort, "U")

            (directory / "notes.md").unlink()
            (directory / "U1.md").write_text("bare\n", encoding="utf-8")
            with self.assertRaisesRegex(
                UnsafeWayfinderState, "unrecognized child filename"
            ):
                next_current_id(effort, "U")

            (directory / "U1.md").unlink()
            (directory / "U1-first.md").write_text("first\n", encoding="utf-8")
            (directory / "U1-duplicate.md").write_text("duplicate\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "duplicate current U"):
                next_current_id(effort, "U")

    def test_contract_keeps_only_current_roles_and_lock_based_allocation(
        self,
    ) -> None:
        for required in (
            "numeric prefix plus a readable filename slug",
            "F# and D# use H2 ledger headings",
            "stable handle within the current Wayfinder representation",
            "Never renumber an existing current record",
            "never allow two current records of one type to share a number",
            "one greater than the highest current same-type identifier",
            "Do not search for or deliberately recycle interior gaps",
            "A retired number is not reserved",
            "`<effort>/.wayfinder-mutation-lock/` directory",
            "Serialize every map, ledger, U#, or E# mutation for an effort",
            "retirement's final reference scan and removal indivisible",
            "U/E files and F/D ledger sections are current durable knowledge",
            "There is no requirement that the record's exact contents already exist in Git",
            "never leave a dangling current link",
            "ordinary highest-current-plus-one rule",
        ):
            self.assertIn(required, self.normalized)

    def test_identifier_reference_scope_is_effort_local_and_links_are_durable(
        self,
    ) -> None:
        for semantic_pattern in (
            r"bare .+ effort-local current-state shorthand",
            r"uniqueness is scoped to current same-type records within that effort",
            r"U#/E# readable filename is its canonical filesystem path",
            r"current F#/D# durable link .+ exact ledger heading",
            r"outside the selected effort needs a reference .+ repository-relative Markdown link",
            r"need not retain .+ temporary current record",
            r"Do not scan the repository or Git history",
        ):
            self.assertRegex(self.normalized, semantic_pattern)

        self.assertIn("U17 blocks D4", self.contract)
        self.assertIn("D4 follows from F8", self.contract)
        self.assertIn("decisions.md#d4--use-a-dedicated-node-group", self.contract)
        self.assertEqual(
            heading_anchor("D", 4, "Use a dedicated node group"),
            "d4--use-a-dedicated-node-group",
        )

    def test_contract_defines_current_records_authority_and_unknown_content_safety(
        self,
    ) -> None:
        for required in (
            "facts.md # optional current F# ledger",
            "decisions.md # optional current D# ledger",
            "unknowns/ # optional independent U# files",
            "evidence/ # optional substantial E# files",
            "If a fresh human or agent must read most supporting artifacts",
            "the effort is over-decomposed and should be reconciled",
            "Every current fact contains at least one truthful provenance mode",
            "`Source`, `Authority`, or `Derived from`",
            "A repeated agent-authored summary is not an independent source",
            "Working assumptions are not facts",
            "An agent-created inference does not become established",
            "accepted | provisional | superseded",
            "Accepted and provisional decisions require actual project authority",
            "Evidence can support a choice but cannot create authority",
            "Revisit when: <required for provisional",
            "## Recognized current state boundary",
            "Wayfinder recognizes only an effort's `map.md`",
            "Content outside that shape is project-owned data",
            "do not interpret it as current Wayfinder state",
            "Unknown project-owned content does not by itself block independent current work",
            "real target or ancestor collision",
            "semantic ambiguity in a recognized current container",
            "Preserve every unknown byte when stopping",
            "Retiring a fact or decision removes only its selected H2 section",
            "Remove an otherwise empty `facts.md` or `decisions.md`",
            "Do not implement automatic ledger sharding",
            "arbitrary F#/D# file-count rule",
        ):
            self.assertIn(required, self.normalized)

    def test_fact_corrections_update_the_same_scoped_fact_in_place(self) -> None:
        for required in (
            "Treat each F# as the current canonical statement of one scoped factual conclusion",
            "same subject, corrected value or scope",
            "update that F# in place",
            "Do not create a new F# merely to preserve history",
            "otherwise Git owns the history",
            "only for an independently useful fact with distinct meaning or scope",
            "mark the existing fact `disputed` or `stale` rather than creating another established fact",
            "Keep a `superseded` decision only while it adds current navigational value",
        ):
            self.assertIn(required, self.normalized)

    def test_contract_protects_sensitive_data_and_unknown_project_content(
        self,
    ) -> None:
        for required in (
            "Never persist secrets, tokens, private keys, raw credentials",
            "sensitive command output",
            "unnecessary personal data",
            "raw transcripts",
            "private agent memory",
            "optional `facts.md` and `decisions.md` ledgers",
            "canonical U#/E# files below `unknowns/` and `evidence/`",
            "mutate or silently normalize it",
            "Lifecycle, provider repair, and projection regeneration treat all `.agent-wayfinder/` content as opaque project-owned data",
        ):
            self.assertIn(required, self.normalized)

    def test_effort_lifecycle_remains_map_owned_and_progressive(self) -> None:
        for required in (
            "- Status: current | completed | abandoned | superseded",
            "This single line is the effort lifecycle representation",
            "an explicit `current` match outranks a similarly named historical match",
            "Read a historical map when it is directly named",
            "An older map without a status remains valid",
            "replace its ready frontier and next work with none for that effort",
        ):
            self.assertIn(required, self.normalized)

        fixture = FIXTURES / "wayfinder-settlement/.agent-wayfinder"
        completed = (fixture / "wayfinder-lifecycle-completed/map.md").read_text()
        abandoned = (fixture / "wayfinder-lifecycle-abandoned/map.md").read_text()
        superseded = (fixture / "wayfinder-lifecycle-superseded/map.md").read_text()
        self.assertIn("- Status: completed", completed)
        self.assertIn("- Status: abandoned", abandoned)
        self.assertIn("- Status: superseded", superseded)
        for historical in (completed, abandoned, superseded):
            self.assertIn("None for this effort.", historical)
        self.assertIn("../settled-provider-direction/map.md", superseded)

    def test_contract_preserves_specialist_results_without_copying_methods(
        self,
    ) -> None:
        for required in (
            "## Specialist result boundary",
            "continue directly or load one materially useful specialist",
            "Specialists own their methods and native artifacts",
            "Do not copy a specialist method, transcript, or temporary bookkeeping",
            "Create no separate specialist continuity record",
            "accepted D#, specification, or implementation ticket",
            "no durable Wayfinder state is needed",
        ):
            self.assertIn(required, self.normalized)
        for duplicated_method in (
            "Form 3–5 ranked, falsifiable hypotheses",
            "Compare only viable alternatives",
            "Use primary sources for consequential",
        ):
            self.assertNotIn(duplicated_method, self.contract)

    def test_contract_structures_territory_and_converges_without_hierarchy(
        self,
    ) -> None:
        for required in (
            "## Semantic territory and effort identity",
            "authoritative project structure",
            "Otherwise establish it directly when current context supports it confidently",
            "Territory is provisional, adaptive, and judgment-based",
            "challenge incomplete framing",
            "must not silently broaden the user's goal, delegated authority, or implementation scope",
            "If structural ambiguity remains",
            "state contract does not own that method",
            "before substantial U/E/F/D state accumulates",
            "## Territory",
            "A semantic area is settled",
            "proper canonical owner",
            "Completed efforts should normally shrink",
        ):
            self.assertIn(required, self.normalized)

    def test_contract_and_runtime_define_an_adaptive_default_map_shape(self) -> None:
        for required in (
            "## Default map shape",
            "strong defaults, not a rigid schema",
            "predictable headings improve scanning and re-entry",
            "`## Destination` — Desired endpoint plus material scope or "
            "authority boundary",
            "`## Territory` — Major areas, ownership or operating constraints, "
            "and important relationships or seams",
            "one sentence, a few bullets, or a compact table",
            "`## Current state` — The smallest truthful summary required for re-entry",
            "authoritative roadmap, specification, ADR, or tracker",
            "`## Blockers and dependencies` — Only material constraints on progress",
            "`## Ready frontier` — Coherent work that can proceed now, what "
            "remains blocked, and the next meaningful milestone or handoff",
            "`## Key links` — Only the few canonical artifacts needed for continuation",
            "combined, renamed, or omitted only when its purpose is genuinely "
            "inapplicable or another structure is materially clearer",
            "Empty sections must not be created merely to satisfy the outline",
            "must not duplicate authoritative roadmaps, specifications, trackers, "
            "facts, decisions, evidence records, generated graphs, or detailed backlogs",
            "`Current phase` is not universal",
            "place that information in `Current state`",
            "`Current position` heading when that materially improves navigation",
        ):
            self.assertIn(required, self.normalized)

        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        self.assertIn(
            "Apply the contract's default map shape when applicable; omit empty headings, "
            "allow a materially clearer equivalent, and never copy canonical plans.",
            runtime,
        )

    def test_runtime_and_contract_promote_only_continuation_worthy_unknowns(
        self,
    ) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        promotion_rule = (
            "A precise question becomes U# when preserving it while unanswered could "
            "materially improve a later developer’s ability to make or evaluate a decision."
        )
        for required in (
            "Map uncertainty broadly, then promote selectively",
            promotion_rule,
            "human or project authority",
            "external owner or approval",
            "multiple downstream areas or a meaningful seam",
            "Ordinary research or debugging fog",
            "does not by itself justify a U#",
        ):
            self.assertIn(required, runtime)

        for required in (
            promotion_rule,
            "`unknown`: a precise unresolved question preserved independently while unanswered because it could materially improve a later developer’s ability to make or evaluate a decision",
            "human or project authority",
            "external owner or approval",
            "multiple downstream areas or a meaningful seam",
            "Keep incidental, routine, easily reconstructed, or merely unspecified detail in the map",
            "Never create a U# from a template, precision, or item count alone",
        ):
            self.assertIn(required, self.normalized)

    def test_runtime_and_contract_define_progressive_loading_and_authority(
        self,
    ) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        self.assertIn(
            "Live source and accepted project artifacts outrank stale map state.",
            runtime,
        )
        for progressive_loading_rule in (
            "Route from the request first",
            "Read the relevant `map.md`",
            "low-resolution orientation",
            "Follow only links needed for the current question or work",
            "do not load unrelated ledger sections or every U/E artifact",
            "Derive the current frontier from the map and any linked native ticket source",
        ):
            self.assertIn(progressive_loading_rule, self.normalized)

        self.assertIn(
            "map owns current state, blockers, dependencies, frontier, and next work",
            runtime,
        )
        for surface in (runtime, self.normalized):
            self.assertIn(
                "Durable Wayfinder state can record authority; it cannot create authority.",
                surface,
            )

    def test_runtime_and_contract_exclude_volatile_git_observations_but_keep_constraints(
        self,
    ) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        for runtime_rule in (
            "Inspect Git/session state when useful for safe execution",
            "do not normally persist volatile observations",
            "Retain durable Git constraints and dependencies under the state contract",
        ):
            self.assertIn(runtime_rule, runtime)

        for volatile_observation in (
            "current branch",
            "HEAD commit",
            "dirty working-tree status",
            "ahead/behind status",
        ):
            self.assertIn(volatile_observation, self.normalized)
        for durable_constraint in (
            "work is authorized only on a named branch",
            "a branch must remain untouched",
            "a particular commit is the required baseline",
            "another branch contains implementation required for continuation",
        ):
            self.assertIn(durable_constraint, self.normalized)

        self.assertIn(
            "Inspect this information when useful for safe execution", self.normalized
        )
        self.assertIn("normally do not persist", self.normalized)
        self.assertIn(
            "Persist it when it represents a durable constraint or dependency",
            self.normalized,
        )

    def test_runtime_and_contract_distinguish_map_fog_from_durable_unknowns(
        self,
    ) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        for required in (
            "Establish the destination and enough relevant territory to orient the effort before substantial decomposition.",
            "Precision alone is insufficient",
            "Not yet specified",
        ):
            self.assertIn(required, runtime)

        for required in (
            "Establish the destination and enough relevant territory to orient the effort before substantial decomposition.",
            "Keep incidental, routine, easily reconstructed, or merely unspecified detail in the map",
            "Keep low-value fog under `Not yet specified`",
            "Precision alone is insufficient",
        ):
            self.assertIn(required, self.normalized)

    def test_resolution_modes_define_sufficient_evidence_or_authority(self) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        rule = (
            "The resolution method determines what evidence or authority is sufficient "
            "to answer the question."
        )
        for surface in (runtime, self.normalized):
            self.assertIn(rule, surface)
            self.assertIn("human clarification", surface)
            self.assertIn("research", surface)
            self.assertIn("prototype", surface)

        for required in (
            "cannot be supplied by agent inference or substituted research",
            "appropriate source evidence",
            "observed or experimental evidence",
            "Running a named method is not itself resolution",
        ):
            self.assertIn(required, self.normalized)

    def test_durable_state_records_but_cannot_create_authority(self) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        authority_rule = (
            "Durable Wayfinder state can record authority; it cannot create authority."
        )
        for surface in (runtime, self.normalized):
            self.assertIn(authority_rule, surface)
            self.assertIn("valid delegated scope", surface)

        self.assertIn(
            "An agent-authored map, U#, E#, F#, D#, or note is not an authority source",
            self.normalized,
        )

    def test_answered_unknown_retires_while_authoritative_disposition_stays_open(
        self,
    ) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        gate = (
            "Answer the consequential U#, or canonically record the responsible authority’s "
            "explicit acceptance of the remaining uncertainty for that boundary."
        )
        self.assertIn(gate, runtime)
        self.assertIn("remains factually unanswered", runtime)
        self.assertIn("only the named boundary", runtime)
        self.assertIn("question remains unanswered", self.normalized)
        self.assertIn("unblock only that boundary", self.normalized)
        for surface in (runtime, self.normalized):
            self.assertIn("The ready frontier is the set of coherent scopes", surface)
            self.assertIn("answered or explicitly dispositioned", surface)
            self.assertIn("keep the U# open", surface)

        for required in (
            "An answered U# is no longer current unknown state",
            "reconcile affected current references and dependencies, then retire the U#",
            "Do not retain a resolved U# solely for history; Git owns history",
            "Answering a U# need not create F# or D# before retirement",
            "A current U# remains open until sufficient evidence or authority answers it and it is retired",
            "An empty `unknowns/` directory has no semantic meaning",
            "not a current unknown, blocker, dependency, or frontier item",
            "requires neither creation nor removal",
        ):
            self.assertIn(required, self.normalized)

        template_match = re.search(
            r"Use U# when a question is consequential enough to track independently:\s*"
            r"```markdown\n(?P<body>.*?)\n```",
            self.contract,
            re.DOTALL,
        )
        self.assertIsNotNone(template_match)
        assert template_match is not None
        self.assertEqual(
            re.findall(r"(?m)^- Status:.*$", template_match.group("body")),
            ["- Status: open"],
        )
        self.assertNotIn("- Status: open | resolved", self.contract)
        self.assertNotIn("mark it `resolved`", self.contract)
        self.assertNotIn("Status: accepted uncertainty", self.contract)

    def test_runtime_and_contract_expose_an_unblocked_ready_frontier(self) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        for required in (
            "coherent ready frontier",
            "one or more ready scopes",
            "without advancing work that remains dependency-blocked",
            "Each Implementation handoff",
        ):
            self.assertIn(required, runtime)

        for required in (
            "coherent ready frontier",
            "List ready scopes only when useful",
            "dependency-blocked work",
            "one coherent scope at a time",
        ):
            self.assertIn(required, self.normalized)

    def test_runtime_and_contract_surface_only_evidence_backed_navigation_shape(
        self,
    ) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        for required in (
            "When dependency evidence is sufficient, surface the navigation shape concisely",
            "critical path",
            "independent parallel work",
            "off-path dependency",
            "external lead time",
            "Do not infer a critical path from an unordered backlog or incomplete evidence",
        ):
            self.assertIn(required, runtime)

        for required in (
            "When evidence establishes execution order",
            "critical path",
            "independent parallel work",
            "off-path dependency",
            "external lead time",
            "Never manufacture a critical path from an unordered backlog or incomplete dependency evidence",
        ):
            self.assertIn(required, self.normalized)

    def test_authored_installed_and_generated_surfaces_are_consistent(self) -> None:
        self.assertEqual(CONTRACT.read_bytes(), INSTALLED_CONTRACT.read_bytes())
        runtime = RUNTIME.read_text(encoding="utf-8")
        generated = GENERATED_SKILL.read_text(encoding="utf-8")
        generated_body = generated.split("\n---\n", 1)[1]
        self.assertEqual(runtime, generated_body)
        normalized_runtime = " ".join(runtime.split())
        for required in (
            "## Core invariants",
            "## Establish territory",
            "## Resolve the frontier progressively",
            "## Reconcile and hand off",
            "Territory is provisional, adaptive, and judgment-based",
            "Optional F/D ledger sections and U/E artifacts preserve only useful current knowledge",
            "Create a separate artifact because it is an independently useful coordination or retrieval unit",
            "Continue directly when the frontier can be resolved safely",
            "Discovery",
            "Debugging",
            "Research",
            "Prototype",
            "Domain Modeling",
            "create no framework continuity record",
            "Interpret and mutate only recognized current Wayfinder state",
            "Preserve unknown project-owned content without interpreting it",
            "continue independent current work",
            "Use `to-tickets`",
            "Verification follows execution",
            "preferred structural fallback",
            "before substantial U/E/F/D accumulates",
            "do not reload Domain Modeling",
            "later authoritative evidence materially invalidates",
            "ordinary fog within coherent territory",
            "If the state contract is unavailable",
        ):
            self.assertIn(required, normalized_runtime)

        for contract_only_detail in (
            ".wayfinder-mutation-lock",
            "highest currently present",
            "retired number",
            "final scan and removal",
        ):
            self.assertNotIn(contract_only_detail, normalized_runtime)


if __name__ == "__main__":
    unittest.main()
