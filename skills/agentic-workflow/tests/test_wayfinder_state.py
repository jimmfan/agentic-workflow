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
CURRENT_ID = re.compile(r"^([UEFD])([1-9][0-9]*)-([^.]+)\.md$")


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
    lock_attempts: int = 1_000,
) -> Path:
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


def retire_current_child(
    effort: Path,
    target: Path,
    *,
    before_final_check: Callable[[], None] | None = None,
    lock_attempts: int = 1_000,
) -> bool:
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
            raise UnsafeWayfinderState("current references appeared during reconciliation")

        target.unlink()
        parent = target.parent
        if not any(parent.iterdir()):
            parent.rmdir()
        return True


class WayfinderStateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = CONTRACT.read_text(encoding="utf-8")
        self.normalized = " ".join(self.contract.split())

    def test_current_state_allocation_skips_gaps_and_may_reuse_retired_highest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            first = create_current_child(effort, "D", "first", "first\n")
            second = create_current_child(effort, "D", "second", "second\n")
            third = create_current_child(effort, "D", "third", "third\n")
            first_before = first.read_bytes()
            third_before = third.read_bytes()

            self.assertEqual(
                (first.name, second.name, third.name),
                ("D1-first.md", "D2-second.md", "D3-third.md"),
            )
            self.assertTrue(retire_current_child(effort, second))
            fourth = create_current_child(effort, "D", "fourth", "fourth\n")
            self.assertEqual(fourth.name, "D4-fourth.md")

            self.assertTrue(retire_current_child(effort, fourth))
            replacement = create_current_child(effort, "D", "replacement", "new meaning\n")

            self.assertEqual(replacement.name, "D4-replacement.md")
            self.assertEqual(first.read_bytes(), first_before)
            self.assertEqual(third.read_bytes(), third_before)
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
            effort = root / ".wayfinder/provider-state"
            unknown = effort / "unknowns/U17-provider-tracker-state.md"
            evidence = effort / "evidence/E12-provider-configuration.md"
            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                retire_current_child(effort, unknown)

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
                    "Supported by: [source.txt](../../../source.txt)",
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
            self.assertTrue(retire_current_child(effort, evidence))
            self.assertTrue(retire_current_child(effort, unknown))
            self.assertFalse(retire_current_child(effort, evidence))
            source_link = (fact.parent / "../../../source.txt").resolve()
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

    def test_resolved_unknown_can_settle_to_map_only(self) -> None:
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
            (directory / "notes.md").write_text("not a canonical child\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "unrecognized child filename"):
                next_current_id(effort, "U")

            (directory / "notes.md").unlink()
            (directory / "U1.md").write_text("bare\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "unrecognized child filename"):
                next_current_id(effort, "U")

            (directory / "U1.md").unlink()
            (directory / "U1-first.md").write_text("first\n", encoding="utf-8")
            (directory / "U1-duplicate.md").write_text("duplicate\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "duplicate current U"):
                next_current_id(effort, "U")

    def test_contract_keeps_only_current_roles_and_no_allocation_primitive(self) -> None:
        for required in (
            "numeric prefix plus a readable filename slug",
            "stable handle within the current Wayfinder representation",
            "Never renumber an existing current record",
            "never allow two current records of one type to share a number",
            "one greater than the highest currently present identifier",
            "Do not search for or deliberately recycle interior gaps",
            "A retired number is not reserved",
            "`<effort>/.wayfinder-mutation-lock/` directory",
            "Serialize every map or child mutation for an effort",
            "final reference scan and removal indivisible",
            "U/E/F/D files are current durable knowledge",
            "There is no requirement that the child's exact contents already exist in Git",
            "never leave a dangling current link",
            "ordinary highest-current-plus-one rule",
        ):
            self.assertIn(required, self.normalized)
        self.assertNotIn("`allocation.md`", self.contract)
        self.assertNotIn("compact retired detail", self.contract)

    def test_identifier_reference_scope_is_effort_local_and_links_are_durable(self) -> None:
        for semantic_pattern in (
            r"bare .+ effort-local current-state shorthand",
            r"uniqueness is scoped to current same-type records within that effort",
            r"readable filename.+ canonical filesystem path",
            r"outside the selected effort .+ repository-relative Markdown link",
            r"need not retain .+ temporary U/E/F/D child",
            r"Do not scan the repository or Git history",
        ):
            self.assertRegex(self.normalized, semantic_pattern)

        self.assertIn("U17 resolved by F8", self.contract)
        self.assertIn("D4 follows from F8", self.contract)
        self.assertIn("D4-use-dedicated-node-group.md", self.contract)

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

        fixture = FIXTURES / "wayfinder-settlement/.wayfinder"
        completed = (fixture / "wayfinder-lifecycle-completed/map.md").read_text()
        abandoned = (fixture / "wayfinder-lifecycle-abandoned/map.md").read_text()
        superseded = (fixture / "wayfinder-lifecycle-superseded/map.md").read_text()
        self.assertIn("- Status: completed", completed)
        self.assertIn("- Status: abandoned", abandoned)
        self.assertIn("- Status: superseded", superseded)
        for historical in (completed, abandoned, superseded):
            self.assertIn("None for this effort.", historical)
        self.assertIn("../settled-provider-direction/map.md", superseded)

    def test_contract_preserves_specialist_results_without_copying_methods(self) -> None:
        for required in (
            "## Specialist result boundary",
            "continue directly or load one materially useful specialist",
            "Specialists own their methods and native artifacts",
            "Do not copy a specialist method, transcript, or temporary bookkeeping",
            "No DEC, IMP, DBG, or replacement record is allocated",
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

    def test_contract_structures_territory_and_converges_without_hierarchy(self) -> None:
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
        for forbidden in (
            "identity/unknowns",
            "networking/decisions",
            "├── identity",
            "## Identity",
        ):
            self.assertNotIn(forbidden, self.contract)

    def test_runtime_and_contract_promote_only_continuation_worthy_unknowns(self) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        promotion_rule = (
            "A precise question becomes U# when preserving the question or its eventual "
            "answer could materially improve a later developer’s ability to make or "
            "evaluate a decision."
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
            "`unknown`: a precise unresolved question preserved independently because its question or eventual answer could materially improve a later developer’s ability to make or evaluate a decision",
            "human or project authority",
            "external owner or approval",
            "multiple downstream areas or a meaningful seam",
            "Keep incidental, routine, easily reconstructed, or merely unspecified detail in the map",
            "Never create a U# from a template, precision, or item count alone",
        ):
            self.assertIn(required, self.normalized)

    def test_runtime_and_contract_distinguish_map_fog_from_durable_unknowns(self) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        for required in (
            "Establish the destination and enough relevant territory to orient the effort before substantial decomposition.",
            "Precision alone is insufficient",
            "Not yet specified",
        ):
            self.assertIn(required, runtime)

        for required in (
            "Establish the destination and enough relevant territory to orient the effort before substantial decomposition.",
            "In-scope fog or unresolved detail that does not currently justify independent U# tracking.",
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
        authority_rule = "Durable Wayfinder state can record authority; it cannot create authority."
        for surface in (runtime, self.normalized):
            self.assertIn(authority_rule, surface)
            self.assertIn("valid delegated scope", surface)

        self.assertIn(
            "An agent-authored map, U#, E#, F#, D#, or note is not an authority source",
            self.normalized,
        )

    def test_answer_or_authoritative_disposition_can_unblock_only_the_named_boundary(self) -> None:
        runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
        gate = (
            "Answer the consequential U#, or canonically record the responsible authority’s "
            "explicit acceptance of the remaining uncertainty for that boundary."
        )
        for surface in (runtime, self.normalized):
            self.assertIn(gate, surface)
            self.assertIn("The ready frontier is the set of coherent scopes", surface)
            self.assertIn("answered or explicitly dispositioned", surface)
            self.assertIn("remains factually unanswered", surface)
            self.assertIn("does not become resolved", surface)
            self.assertIn("only the named boundary", surface)

        self.assertIn("- Status: open | resolved", self.contract)
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
            "one or more independently ready scopes",
            "dependency-blocked work",
            "one coherent scope at a time",
        ):
            self.assertIn(required, self.normalized)

    def test_runtime_and_contract_surface_only_evidence_backed_navigation_shape(self) -> None:
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
            "Optional U/E/F/D preserves only independently useful knowledge",
            "Continue directly when the frontier can be resolved safely",
            "Discovery",
            "Debugging",
            "Research",
            "Prototype",
            "Domain Modeling",
            "create no framework continuity record",
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
