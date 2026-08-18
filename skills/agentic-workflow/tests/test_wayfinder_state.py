from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import re
import shutil
import subprocess
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
CURRENT_ID = re.compile(r"^([UEFD])([1-9][0-9]*)(?:-[^.]+)?\.md$")


class UnsafeWayfinderState(RuntimeError):
    pass


def current_ids(effort: Path, kind: str) -> list[int]:
    directory = effort / TYPE_DIRECTORIES[kind]
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise UnsafeWayfinderState(f"unsafe {kind} directory")

    result: list[int] = []
    for child in directory.iterdir():
        if child.is_symlink() or not child.is_file():
            raise UnsafeWayfinderState(f"unsafe child path: {child.name}")
        match = CURRENT_ID.fullmatch(child.name)
        if match is None or match.group(1) != kind:
            raise UnsafeWayfinderState(f"unrecognized child filename: {child.name}")
        result.append(int(match.group(2)))
    if len(result) != len(set(result)):
        raise UnsafeWayfinderState(f"duplicate current {kind} identifier")
    return result


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
) -> Path:
    if before_lock is not None:
        before_lock()
    with effort_mutation_lock(effort):
        directory = effort / TYPE_DIRECTORIES[kind]
        directory.mkdir(parents=True, exist_ok=True)
        candidate = next_current_id(effort, kind)
        path = directory / f"{kind}{candidate}-{slug}.md"
        with path.open("x", encoding="utf-8") as handle:
            handle.write(body)
        return path


def current_markdown(effort: Path, *, excluding: Path | None = None) -> dict[Path, bytes]:
    result: dict[Path, bytes] = {}
    for path in effort.rglob("*.md"):
        if path == excluding:
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


def git_history_contains_current(repository: Path, target: Path) -> bool:
    relative = target.relative_to(repository).as_posix()
    commits = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", relative],
        cwd=repository,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.splitlines()
    current = target.read_bytes()
    for commit in commits:
        historical = subprocess.run(
            ["git", "show", f"{commit}:{relative}"],
            cwd=repository,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if historical.returncode == 0 and historical.stdout == current:
            return True
    return False


def retire_current_child(
    effort: Path,
    target: Path,
    *,
    repository: Path,
    lock_attempts: int = 1_000,
) -> bool:
    with effort_mutation_lock(effort, attempts=lock_attempts):
        if not target.exists():
            return False
        if not git_history_contains_current(repository, target):
            raise UnsafeWayfinderState(
                "retiring file's current content is absent from recoverable Git history"
            )
        references = references_to(effort, target)
        if references:
            raise UnsafeWayfinderState(f"current references remain: {references}")
        target.unlink()
        parent = target.parent
        if not any(parent.iterdir()):
            parent.rmdir()
        return True


def commit_fixture(repository: Path, message: str) -> None:
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(["git", "add", "."], cwd=repository, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Wayfinder Test",
            "-c",
            "user.email=wayfinder@example.invalid",
            "commit",
            "-qm",
            message,
        ],
        cwd=repository,
        check=True,
    )


class WayfinderStateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = CONTRACT.read_text(encoding="utf-8")
        self.normalized = " ".join(self.contract.split())

    def test_current_state_allocation_reuses_retired_highest_id_without_renumbering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "project"
            effort = repository / ".agent-workflow-state/wayfinder/effort"
            first = create_current_child(effort, "D", "first", "first\n")
            second = create_current_child(effort, "D", "second", "second\n")
            first_before = first.read_bytes()
            commit_fixture(repository, "current decisions")

            self.assertEqual((first.name, second.name), ("D1-first.md", "D2-second.md"))
            self.assertTrue(retire_current_child(effort, second, repository=repository))
            replacement = create_current_child(effort, "D", "replacement", "new meaning\n")

            self.assertEqual(replacement.name, "D2-replacement.md")
            self.assertEqual(first.read_bytes(), first_before)
            self.assertFalse((effort / "allocation.md").exists())

    def test_atomic_effort_lock_serializes_simultaneous_different_slugs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            barrier = threading.Barrier(2)
            created: list[Path] = []
            errors: list[BaseException] = []

            def create(slug: str) -> None:
                try:
                    created.append(
                        create_current_child(
                            effort,
                            "D",
                            slug,
                            f"{slug}\n",
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
            self.assertEqual({path.name[:2] for path in created}, {"D1", "D2"})
            self.assertEqual(len(current_ids(effort, "D")), 2)
            self.assertFalse((effort / ".wayfinder-mutation-lock").exists())

    def test_retirement_requires_reconciled_references_and_is_idempotent(self) -> None:
        fixture = FIXTURES / "wayfinder-reference-settlement"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            shutil.copytree(fixture, root)
            effort = root / ".agent-workflow-state/wayfinder/provider-state"
            unknown = effort / "unknowns/U17-provider-tracker-state.md"
            evidence = effort / "evidence/E12-provider-configuration.md"
            commit_fixture(root, "initial investigation")

            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                retire_current_child(effort, unknown, repository=root)

            (effort / "map.md").write_text(
                "# Provider state settlement\n\n- Status: current\n\n"
                "## Current state\n\n[F8](facts/F8-provider-needs-no-tracker.md) and "
                "[D4](decisions/D4-use-local-runtime.md) remain current.\n",
                encoding="utf-8",
            )
            fact = effort / "facts/F8-provider-needs-no-tracker.md"
            fact.write_text(
                fact.read_text(encoding="utf-8").replace(
                    "Supported by: E12",
                    "Supported by: [source.txt](../../../../source.txt)",
                ),
                encoding="utf-8",
            )
            decision = effort / "decisions/D4-use-local-runtime.md"
            decision.write_text(
                decision.read_text(encoding="utf-8").replace("Related: U17, F8", "Related: F8"),
                encoding="utf-8",
            )
            unknown.write_text(
                unknown.read_text(encoding="utf-8")
                .replace("Related: E12, F8, D4", "Related: F8, D4")
                .replace("E12 establishes that tracker state is not required.",
                         "The answer is recorded in current state."),
                encoding="utf-8",
            )
            evidence.write_text(
                evidence.read_text(encoding="utf-8").replace("Related: U17, F8", "Related: F8"),
                encoding="utf-8",
            )
            commit_fixture(root, "reconcile current references")

            self.assertTrue(retire_current_child(effort, evidence, repository=root))
            self.assertTrue(retire_current_child(effort, unknown, repository=root))
            self.assertFalse(retire_current_child(effort, evidence, repository=root))
            source_link = (fact.parent / "../../../../source.txt").resolve()
            self.assertEqual(source_link, (root / "source.txt").resolve())
            self.assertTrue(source_link.is_file())
            self.assertNotIn("U17", decision.read_text(encoding="utf-8"))

    def test_unrecoverable_history_or_unavailable_lock_retains_record(self) -> None:
        fixture = FIXTURES / "wayfinder-reference-settlement"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            shutil.copytree(fixture, root)
            effort = root / ".agent-workflow-state/wayfinder/provider-state"
            unknown = effort / "unknowns/U17-provider-tracker-state.md"
            commit_fixture(root, "initial investigation")
            unknown.write_text(
                unknown.read_text(encoding="utf-8") + "\nUncommitted current detail.\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current content"):
                retire_current_child(effort, unknown, repository=root)
            self.assertTrue(unknown.exists())

            (effort / ".wayfinder-mutation-lock").mkdir()
            with self.assertRaisesRegex(UnsafeWayfinderState, "lock is unavailable"):
                retire_current_child(effort, unknown, repository=root, lock_attempts=1)
            self.assertTrue(unknown.exists())

    def test_resolved_unknown_can_settle_to_map_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "project"
            effort = repository / ".agent-workflow-state/wayfinder/map-only"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            map_path = effort / "map.md"
            unknown = unknowns / "U1-tracker-state.md"
            map_path.write_text("# Map only\n\nU1 remains open.\n", encoding="utf-8")
            unknown.write_text("# U1: Tracker state?\n", encoding="utf-8")
            commit_fixture(repository, "record investigation")

            map_path.write_text(
                "# Map only\n\nTracker state is not required.\n",
                encoding="utf-8",
            )
            self.assertTrue(retire_current_child(effort, unknown, repository=repository))

            self.assertEqual(
                [path.relative_to(effort).as_posix() for path in effort.iterdir()],
                ["map.md"],
            )

    def test_unsafe_current_paths_block_allocation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            directory = effort / "unknowns"
            directory.mkdir(parents=True)
            (directory / "notes.md").write_text("not a canonical child\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "unrecognized child filename"):
                next_current_id(effort, "U")

            (directory / "notes.md").unlink()
            (directory / "U1-first.md").write_text("first\n", encoding="utf-8")
            (directory / "U1-duplicate.md").write_text("duplicate\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "duplicate current U"):
                next_current_id(effort, "U")

    def test_contract_keeps_only_current_roles_and_no_allocation_primitive(self) -> None:
        for required in (
            "Never renumber an existing current record",
            "Assign one greater than the highest current filename",
            "A retired number is not reserved",
            "atomically creating the empty `<effort>/.wayfinder-mutation-lock/` directory",
            "reject duplicate current numbers",
            "U/E/F/D files are current durable knowledge",
            "recoverable Git history contains the retiring file's current content",
            "never leave a dangling current link",
            "The retired number becomes available",
        ):
            self.assertIn(required, self.normalized)
        self.assertNotIn("`allocation.md`", self.contract)
        self.assertNotIn("compact retired detail", self.contract)

    def test_effort_lifecycle_remains_map_owned_and_progressive(self) -> None:
        for required in (
            "- Status: current | completed | abandoned | superseded",
            "This single line is the effort lifecycle representation",
            "an explicit `current` match outranks a similarly named historical match",
            "Read a historical map when it is directly named",
            "An older map without a status remains valid",
            "replace `Next work` with none for that effort",
        ):
            self.assertIn(required, self.normalized)

        fixture = FIXTURES / "wayfinder-settlement/.agent-workflow-state/wayfinder"
        completed = (fixture / "wayfinder-lifecycle-completed/map.md").read_text()
        abandoned = (fixture / "wayfinder-lifecycle-abandoned/map.md").read_text()
        superseded = (fixture / "wayfinder-lifecycle-superseded/map.md").read_text()
        self.assertIn("- Status: completed", completed)
        self.assertIn("- Status: abandoned", abandoned)
        self.assertIn("- Status: superseded", superseded)
        for historical in (completed, abandoned, superseded):
            self.assertIn("None for this effort.", historical)
        self.assertIn("../settled-provider-direction/map.md", superseded)

    def test_authored_installed_and_generated_surfaces_are_consistent(self) -> None:
        self.assertEqual(CONTRACT.read_bytes(), INSTALLED_CONTRACT.read_bytes())
        runtime = RUNTIME.read_text(encoding="utf-8")
        generated = GENERATED_SKILL.read_text(encoding="utf-8")
        generated_body = generated.split("\n---\n", 1)[1]
        self.assertEqual(runtime, generated_body)
        normalized_runtime = " ".join(runtime.split())
        for required in (
            "Status: current | completed | abandoned | superseded",
            "never renumber a current record",
            "A retired number may be reused",
            "empty transient `<effort>/.wayfinder-mutation-lock/` directory",
            "different slugs from claiming the same number",
            "U/E/F/D files are current knowledge roles",
            "After removal its number is no longer reserved",
        ):
            self.assertIn(required, normalized_runtime)


if __name__ == "__main__":
    unittest.main()
