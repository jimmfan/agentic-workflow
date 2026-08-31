from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import sys
from pathlib import Path
from unittest import mock

from _test_support import (
    LIFECYCLE,
    MANAGED_BEGIN,
    MANAGED_END,
    PACKAGE_ROOT,
    REPOSITORY_ROOT,
    ProjectTestCase,
    load_module,
    run_script,
)


RETAINED_SKILLS = {
    "code-review",
    "codebase-design",
    "domain-modeling",
    "grilling",
    "implement",
    "prototype",
    "research",
    "tdd",
    "to-spec",
    "to-tickets",
    "wayfinder",
    "workflow-debugging",
    "workflow-discovery",
    "workflow-implementation",
    "workflow-verification",
}

REMOVED_SKILLS = {"setup-matt-pocock-skills", "teach", "triage"}

LEGACY_PROVIDER_SKILLS = RETAINED_SKILLS - {
    "workflow-debugging",
    "workflow-discovery",
    "workflow-implementation",
    "workflow-verification",
} | REMOVED_SKILLS

PINNED_FIXTURE = Path(__file__).parent / "fixtures/pinned-main-installation"
PINNED_MAIN = "29941f3020355928b9d43fe4bbc6c98218bc0c28"
FORMER_PROVIDERS_SHA256 = (
    "989803a05145abc0bad9a2592365cbd8fd9873793846ace4459dde5fc0fa32ae"
)
FROZEN_FIXTURE_PROOF_SHA256 = (
    "e623bb714b26e83b9003588bd670b21374134184c078174ce8386634e865235f"
)


def fixture_snapshot(root: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries.append({"path": relative, "type": "symlink"})
        elif path.is_dir():
            entries.append({"path": relative, "type": "directory"})
        elif path.is_file():
            entries.append(
                {
                    "path": relative,
                    "type": "file",
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
        else:
            entries.append({"path": relative, "type": "special"})
    return entries


def lifecycle_snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    result: dict[str, tuple[object, ...]] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        details = os.lstat(path)
        mode = stat.S_IMODE(details.st_mode)
        if stat.S_ISLNK(details.st_mode):
            result[relative] = ("symlink", mode, os.readlink(path))
        elif stat.S_ISDIR(details.st_mode):
            result[relative] = ("directory", mode)
        elif stat.S_ISREG(details.st_mode):
            result[relative] = ("file", mode, path.read_bytes())
        else:
            result[relative] = ("special", mode)
    return result


def stable_lifecycle_snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    temporary_prefixes = (
        ".agent-workflow-stage-",
        ".agent-workflow-transaction-",
        ".agent-workflow-backup-",
        ".agent-workflow-remove-",
    )
    return {
        path: entry
        for path, entry in lifecycle_snapshot(root).items()
        if not path.split("/", 1)[0].startswith(temporary_prefixes)
    }


def integrity_digest(manifest: dict[str, object]) -> str:
    value = {
        key: manifest[key]
        for key in (
            "schema_version",
            "framework_version",
            "source_revision",
            "external_files",
            "composites",
        )
    }
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def manifest_bytes(manifest: dict[str, object]) -> bytes:
    manifest["integrity_sha256"] = integrity_digest(manifest)
    return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")


def managed_region(path: Path) -> bytes:
    data = path.read_bytes()
    start = data.index(MANAGED_BEGIN) + len(MANAGED_BEGIN)
    end = data.index(MANAGED_END)
    return data[start:end]


def assert_pinned_fixture(test: ProjectTestCase) -> None:
    proof_path = PINNED_FIXTURE / "proof.json"
    test.assertEqual(
        hashlib.sha256(proof_path.read_bytes()).hexdigest(),
        FROZEN_FIXTURE_PROOF_SHA256,
    )
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    test.assertEqual(proof["schema_version"], 1)
    test.assertEqual(proof["source_commit"], PINNED_MAIN)
    test.assertEqual(proof["former_providers_sha256"], FORMER_PROVIDERS_SHA256)
    test.assertEqual(proof["entries"], fixture_snapshot(PINNED_FIXTURE / "project"))
    test.assertEqual(
        hashlib.sha256(
            (
                PINNED_FIXTURE
                / "project/.agent-workflow/providers.json"
            ).read_bytes()
        ).hexdigest(),
        FORMER_PROVIDERS_SHA256,
    )
    test.assertEqual(
        {
            path.name
            for path in (PINNED_FIXTURE / "project/.agents/skills").iterdir()
            if path.is_dir()
        },
        LEGACY_PROVIDER_SKILLS
        | {
            "workflow-debugging",
            "workflow-discovery",
            "workflow-implementation",
            "workflow-verification",
        },
    )


class DirectDistributionTests(ProjectTestCase):
    def load_adopt(self, package: Path, name: str):
        scripts = str(package / "scripts")
        sys.path.insert(0, scripts)
        try:
            return load_module(name, package / "scripts/adopt.py")
        finally:
            sys.path.remove(scripts)

    def package_without_mapping(self, name: str, target: str) -> Path:
        package = self.copy_package(name)
        manifest_path = package / "payload/distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_owned"] = [
            item
            for item in manifest["framework_owned"]
            if item["target"] != target
        ]
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return package

    def test_fresh_install_uses_only_the_direct_curated_payload(self) -> None:
        result = run_script(LIFECYCLE, "install", self.project)
        self.assert_ok(result)

        payload = PACKAGE_ROOT / "payload/skills"
        installed = self.project / ".agents/skills"
        self.assertEqual(
            {path.name for path in installed.iterdir() if path.is_dir()},
            RETAINED_SKILLS,
        )
        for source in payload.rglob("*"):
            if source.is_file():
                target = installed / source.relative_to(payload)
                with self.subTest(target=target):
                    self.assertEqual(target.read_bytes(), source.read_bytes())

        for name in REMOVED_SKILLS:
            self.assertFalse((installed / name).exists())
        self.assertFalse((self.project / ".agent-workflow/providers.json").exists())

        manifest = json.loads(
            (self.project / ".agent-workflow/install-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            set(manifest["external_files"]),
            {
                path.relative_to(self.project).as_posix()
                for path in installed.rglob("*")
                if path.is_file()
            },
        )

    def test_exact_pinned_main_installation_transitions_atomically(self) -> None:
        assert_pinned_fixture(self)
        shutil.copytree(PINNED_FIXTURE / "project", self.project, dirs_exist_ok=True)
        unrelated = self.project / ".agents/skills/project-local/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_bytes(b"project-owned skill\n")
        wayfinder_before = fixture_snapshot(self.project / ".agent-wayfinder")
        agents_before = (self.project / "AGENTS.md").read_bytes()

        result = run_script(LIFECYCLE, "update", self.project)
        self.assert_ok(result)

        installed = self.project / ".agents/skills"
        self.assertEqual(
            {path.name for path in installed.iterdir() if path.is_dir()},
            RETAINED_SKILLS | {"project-local"},
        )
        for name in REMOVED_SKILLS:
            self.assertFalse((installed / name).exists())
        self.assertEqual(unrelated.read_bytes(), b"project-owned skill\n")
        self.assertEqual(
            fixture_snapshot(self.project / ".agent-wayfinder"), wayfinder_before
        )
        self.assertTrue((self.project / "AGENTS.md").read_bytes().endswith(
            agents_before.split(b"<!-- agent-workflow:project-instructions -->\n", 1)[1]
        ))
        self.assertFalse((self.project / ".agent-workflow/providers.json").exists())

        manifest = json.loads(
            (self.project / ".agent-workflow/install-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["schema_version"], 2)
        self.assertRegex(manifest["integrity_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(len(manifest["external_files"]), 34)
        self.assertTrue(
            all(details["created"] for details in manifest["external_files"].values())
        )
        status = run_script(LIFECYCLE, "status", self.project)
        self.assert_ok(status)
        self.assertIn("Agent Workflow: healthy", status.stdout)

    def test_checked_in_projection_equals_the_exact_fixture_transition(self) -> None:
        assert_pinned_fixture(self)
        shutil.copytree(PINNED_FIXTURE / "project", self.project, dirs_exist_ok=True)
        project_agents_before = {
            name: (self.project / name).read_bytes()
            for name in ("AGENTS.md", "CLAUDE.md")
        }
        wayfinder_before = lifecycle_snapshot(self.project / ".agent-wayfinder")

        result = run_script(
            LIFECYCLE,
            "update",
            self.project,
            "--source-revision",
            "unreleased-local-package",
        )
        self.assert_ok(result)

        self.assertEqual(
            lifecycle_snapshot(self.project / ".agent-workflow"),
            lifecycle_snapshot(REPOSITORY_ROOT / ".agent-workflow"),
        )
        self.assertEqual(
            lifecycle_snapshot(self.project / ".agents/skills"),
            lifecycle_snapshot(REPOSITORY_ROOT / ".agents/skills"),
        )
        for name in ("AGENTS.md", "CLAUDE.md"):
            with self.subTest(composite=name):
                self.assertEqual(
                    managed_region(self.project / name),
                    managed_region(REPOSITORY_ROOT / name),
                )
        self.assertEqual(
            lifecycle_snapshot(self.project / ".agent-wayfinder"),
            wayfinder_before,
        )
        self.assertTrue(
            (self.project / "AGENTS.md").read_bytes().endswith(
                project_agents_before["AGENTS.md"].split(
                    b"<!-- agent-workflow:project-instructions -->\n", 1
                )[1]
            )
        )
        self.assertEqual(
            project_agents_before["CLAUDE.md"],
            (self.project / "CLAUDE.md").read_bytes(),
        )

    def test_transition_preserves_each_valid_workflow_created_bit(self) -> None:
        shutil.copytree(PINNED_FIXTURE / "project", self.project, dirs_exist_ok=True)
        manifest_path = self.project / ".agent-workflow/install-manifest.json"
        former = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected: dict[str, bool] = {}
        for index, path in enumerate(sorted(former["external_files"])):
            created = index % 2 == 0
            former["external_files"][path]["created"] = created
            expected[path] = created
        manifest_path.write_text(
            json.dumps(former, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        result = run_script(LIFECYCLE, "update", self.project)
        self.assert_ok(result)

        current = json.loads(manifest_path.read_text(encoding="utf-8"))
        for path, created in expected.items():
            with self.subTest(path=path):
                self.assertEqual(current["external_files"][path]["created"], created)
        provider_files = set(current["external_files"]) - set(expected)
        self.assertEqual(len(provider_files), 30)
        self.assertTrue(
            all(current["external_files"][path]["created"] for path in provider_files)
        )

    def test_valid_stale_and_absent_install_states_are_distinct(self) -> None:
        status = run_script(LIFECYCLE, "status", self.project)
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("repairable", status.stdout)

        exact = PACKAGE_ROOT / "payload/skills/research/SKILL.md"
        preexisting = self.project / ".agents/skills/research/SKILL.md"
        preexisting.parent.mkdir(parents=True)
        preexisting.write_bytes(exact.read_bytes())
        (self.project / ".agent-wayfinder").mkdir()
        self.assert_ok(run_script(LIFECYCLE, "install", self.project))
        manifest_path = self.project / ".agent-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertFalse(
            manifest["external_files"][".agents/skills/research/SKILL.md"][
                "created"
            ]
        )

        manifest["framework_version"] = "0.22.0"
        manifest["source_revision"] = "1" * 40
        manifest_path.write_bytes(manifest_bytes(manifest))
        stale = run_script(LIFECYCLE, "status", self.project)
        self.assertEqual(stale.returncode, 1, stale.stdout + stale.stderr)
        self.assertIn("framework version differs", stale.stdout)
        self.assertIn("source revision differs", stale.stdout)
        self.assert_ok(run_script(LIFECYCLE, "update", self.project))
        self.assert_ok(run_script(LIFECYCLE, "status", self.project))

    def test_invalid_current_install_state_fails_closed_for_every_command(self) -> None:
        base = Path(self.temporary.name) / "valid-install"
        base.mkdir()
        self.assert_ok(run_script(LIFECYCLE, "install", base))
        valid_path = base / ".agent-workflow/install-manifest.json"
        valid_bytes = valid_path.read_bytes()
        valid = json.loads(valid_bytes)

        truncated = json.loads(valid_bytes)
        truncated["external_files"].pop(next(iter(truncated["external_files"])))
        bad_digest = json.loads(valid_bytes)
        bad_digest["integrity_sha256"] = "0" * 64
        schema_bool = json.loads(valid_bytes)
        schema_bool["schema_version"] = True
        schema_float = json.loads(valid_bytes)
        schema_float["schema_version"] = 2.0
        unsafe_path = json.loads(valid_bytes)
        first_key = next(iter(unsafe_path["external_files"]))
        unsafe_path["external_files"]["../unsafe"] = unsafe_path[
            "external_files"
        ].pop(first_key)
        nul_path = json.loads(valid_bytes)
        nul_path["external_files"]["bad\x00path"] = nul_path[
            "external_files"
        ].pop(first_key)
        dot_path = json.loads(valid_bytes)
        dot_path["external_files"]["."] = dot_path["external_files"].pop(first_key)
        surrogate_path = json.loads(valid_bytes)
        surrogate_path["external_files"]["bad\ud800path"] = surrogate_path[
            "external_files"
        ].pop(first_key)
        malformed_entry = json.loads(valid_bytes)
        malformed_entry["external_files"][first_key]["created"] = "yes"
        internal_path = json.loads(valid_bytes)
        internal_path["external_files"][".agent-workflow/owned"] = internal_path[
            "external_files"
        ].pop(first_key)
        composite_path = json.loads(valid_bytes)
        composite_path["external_files"]["AGENTS.md"] = composite_path[
            "external_files"
        ].pop(first_key)
        durable_path = json.loads(valid_bytes)
        durable_path["external_files"][".agent-wayfinder/owned"] = durable_path[
            "external_files"
        ].pop(first_key)
        duplicate = valid_bytes.replace(
            b'{\n  "composites"', b'{\n  "schema_version": 2,\n  "composites"', 1
        )
        mutations = {
            "malformed": b"{not json\n",
            "truncated": json.dumps(truncated).encode("utf-8"),
            "duplicate-key": duplicate,
            "bad-digest": json.dumps(bad_digest).encode("utf-8"),
            "schema-bool": manifest_bytes(schema_bool),
            "schema-float": manifest_bytes(schema_float),
            "unsafe-path": manifest_bytes(unsafe_path),
            "nul-path": manifest_bytes(nul_path),
            "dot-path": manifest_bytes(dot_path),
            "surrogate-path": json.dumps(surrogate_path).encode("utf-8"),
            "invalid-type": json.dumps(
                {**valid, "external_files": []}
            ).encode("utf-8"),
            "malformed-entry": manifest_bytes(malformed_entry),
            "internal-external-path": manifest_bytes(internal_path),
            "composite-external-path": manifest_bytes(composite_path),
            "durable-external-path": manifest_bytes(durable_path),
            "invalid-encoding": b"\xff\xfe\x00",
        }

        for mutation, content in mutations.items():
            for command in ("status", "install", "update", "remove"):
                with self.subTest(mutation=mutation, command=command):
                    project = Path(self.temporary.name) / f"{mutation}-{command}"
                    shutil.copytree(base, project)
                    (project / ".agent-workflow/install-manifest.json").write_bytes(
                        content
                    )
                    before = lifecycle_snapshot(project)
                    result = run_script(LIFECYCLE, command, project)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("invalid install state", result.stdout + result.stderr)
                    self.assertEqual(lifecycle_snapshot(project), before)

    def test_missing_manifest_is_invalid_when_managed_evidence_remains(self) -> None:
        self.assert_ok(run_script(LIFECYCLE, "install", self.project))
        (self.project / ".agent-workflow/install-manifest.json").unlink()
        before = lifecycle_snapshot(self.project)
        for command in ("status", "install", "update", "remove"):
            with self.subTest(command=command):
                result = run_script(LIFECYCLE, command, self.project)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("manifest is absent", result.stdout + result.stderr)
                self.assertEqual(lifecycle_snapshot(self.project), before)

    def test_near_match_former_installations_are_rejected_without_mutation(self) -> None:
        cases = (
            "schema-bool",
            "schema-float",
            "declaration",
            "altered-file",
            "unexpected-descendant",
            "missing-file",
            "symlink",
            "special-entry",
            "unsafe-root",
        )
        for case in cases:
            with self.subTest(case=case):
                project = Path(self.temporary.name) / f"legacy-{case}"
                shutil.copytree(PINNED_FIXTURE / "project", project)
                if case in {"schema-bool", "schema-float"}:
                    manifest_path = project / ".agent-workflow/install-manifest.json"
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    manifest["schema_version"] = (
                        True if case == "schema-bool" else 1.0
                    )
                    manifest_path.write_text(
                        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                elif case == "declaration":
                    declaration = project / ".agent-workflow/providers.json"
                    declaration.write_bytes(declaration.read_bytes() + b"\n")
                elif case == "altered-file":
                    (project / ".agents/skills/research/SKILL.md").write_bytes(
                        b"altered former skill\n"
                    )
                elif case == "unexpected-descendant":
                    (project / ".agents/skills/research/unexpected").mkdir()
                elif case == "missing-file":
                    (project / ".agents/skills/tdd/tests.md").unlink()
                elif case == "symlink":
                    target = project / ".agents/skills/research/SKILL.md"
                    target.unlink()
                    target.symlink_to("agents/openai.yaml")
                elif case == "special-entry":
                    os.mkfifo(project / ".agents/skills/research/special")
                elif case == "unsafe-root":
                    root = project / ".agents/skills/research"
                    outside = Path(self.temporary.name) / f"outside-{case}"
                    shutil.move(root, outside)
                    root.symlink_to(outside, target_is_directory=True)

                before = lifecycle_snapshot(project)
                for command in ("status", "install", "update", "remove"):
                    result = run_script(LIFECYCLE, command, project)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("invalid install state", result.stdout + result.stderr)
                    self.assertEqual(lifecycle_snapshot(project), before)

    def test_retirement_is_atomic_and_requires_safe_deletion_evidence(self) -> None:
        retired = ".agents/skills/tdd/tests.md"
        target = self.project / retired
        self.assert_ok(run_script(LIFECYCLE, "install", self.project))
        package = self.package_without_mapping("retirement-safe", retired)
        updater = package / "scripts/lifecycle.py"

        status = run_script(updater, "status", self.project)
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("safely removable", status.stdout)
        self.assert_ok(run_script(updater, "update", self.project))
        self.assertFalse(target.exists())
        manifest = json.loads(
            (self.project / ".agent-workflow/install-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertNotIn(retired, manifest["external_files"])
        self.assert_ok(run_script(updater, "status", self.project))

        for case in ("preexisting", "changed"):
            with self.subTest(case=case):
                project = Path(self.temporary.name) / f"retirement-{case}"
                project.mkdir()
                candidate = project / retired
                if case == "preexisting":
                    source = PACKAGE_ROOT / "payload/skills/tdd/tests.md"
                    candidate.parent.mkdir(parents=True)
                    candidate.write_bytes(source.read_bytes())
                self.assert_ok(run_script(LIFECYCLE, "install", project))
                if case == "changed":
                    candidate.write_bytes(b"locally changed managed file\n")
                drifted_sibling = project / ".agents/skills/research/SKILL.md"
                drifted_sibling.write_bytes(b"drift that must remain on conflict\n")
                before = lifecycle_snapshot(project)

                conflict_status = run_script(updater, "status", project)
                self.assertEqual(
                    conflict_status.returncode,
                    2,
                    conflict_status.stdout + conflict_status.stderr,
                )
                self.assertIn("safe deletion proof", conflict_status.stdout)
                update = run_script(updater, "update", project)
                self.assertEqual(update.returncode, 2, update.stdout + update.stderr)
                self.assertIn("safe deletion proof", update.stderr)
                self.assertEqual(lifecycle_snapshot(project), before)

    def test_repair_preserves_created_bits_and_remove_preserves_unsafe_content(self) -> None:
        preexisting_path = ".agents/skills/research/SKILL.md"
        created_path = ".agents/skills/tdd/tests.md"
        preexisting = self.project / preexisting_path
        preexisting.parent.mkdir(parents=True)
        preexisting.write_bytes(
            (PACKAGE_ROOT / "payload/skills/research/SKILL.md").read_bytes()
        )
        durable = self.project / ".agent-wayfinder/preserved.txt"
        durable.parent.mkdir()
        durable.write_bytes(b"durable project bytes\n")
        self.assert_ok(run_script(LIFECYCLE, "install", self.project))

        manifest_path = self.project / ".agent-workflow/install-manifest.json"
        before_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertFalse(before_manifest["external_files"][preexisting_path]["created"])
        self.assertTrue(before_manifest["external_files"][created_path]["created"])

        preexisting.unlink()
        created = self.project / created_path
        created.write_bytes(b"drifted framework-created file\n")
        self.assert_ok(run_script(LIFECYCLE, "update", self.project))
        repaired_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertFalse(
            repaired_manifest["external_files"][preexisting_path]["created"]
        )
        self.assertTrue(repaired_manifest["external_files"][created_path]["created"])
        self.assertEqual(
            preexisting.read_bytes(),
            (PACKAGE_ROOT / "payload/skills/research/SKILL.md").read_bytes(),
        )

        created.write_bytes(b"changed after repair\n")
        self.assert_ok(run_script(LIFECYCLE, "remove", self.project))
        self.assertEqual(preexisting.read_bytes(), (
            PACKAGE_ROOT / "payload/skills/research/SKILL.md"
        ).read_bytes())
        self.assertEqual(created.read_bytes(), b"changed after repair\n")
        self.assertEqual(durable.read_bytes(), b"durable project bytes\n")
        self.assertFalse((self.project / ".agent-workflow").exists())
        status = run_script(LIFECYCLE, "status", self.project)
        self.assertEqual(status.returncode, 2, status.stdout + status.stderr)
        self.assertIn("unknown external content", status.stdout)

    def test_composite_repair_preserves_both_created_values(self) -> None:
        replacement = b"late project-authored policy replacement\n"
        for created in (False, True):
            for repair in ("missing", "markerless"):
                with self.subTest(created=created, repair=repair):
                    project = Path(self.temporary.name) / f"composite-{created}-{repair}"
                    project.mkdir()
                    policy = project / "AGENTS.md"
                    if not created:
                        policy.write_bytes(b"pre-existing project policy\n")
                    self.assert_ok(run_script(LIFECYCLE, "install", project))
                    manifest_path = project / ".agent-workflow/install-manifest.json"
                    before = json.loads(manifest_path.read_text(encoding="utf-8"))
                    self.assertIs(before["composites"]["AGENTS.md"]["created"], created)

                    if repair == "missing":
                        policy.unlink()
                    else:
                        policy.write_bytes(replacement)
                    self.assert_ok(run_script(LIFECYCLE, "update", project))

                    after = json.loads(manifest_path.read_text(encoding="utf-8"))
                    self.assertIs(after["composites"]["AGENTS.md"]["created"], created)
                    if repair == "markerless":
                        self.assertIn(replacement, policy.read_bytes())

    def test_late_external_changes_abort_before_transaction_mutation(self) -> None:
        def assert_rejected(
            module,
            project: Path,
            invoke,
            mutate,
            expected: str = "changed at lifecycle mutation boundary",
        ) -> None:
            original = module.apply_external_transaction
            observed: dict[str, dict[str, tuple[object, ...]]] = {}

            def late_change(*args, **kwargs):
                mutate()
                observed["after_user_change"] = stable_lifecycle_snapshot(project)
                return original(*args, **kwargs)

            with (
                mock.patch.object(module, "apply_external_transaction", late_change),
                self.assertRaises(module.AdoptionError) as raised,
            ):
                invoke()
            self.assertIn(expected, str(raised.exception))
            self.assertEqual(
                stable_lifecycle_snapshot(project), observed["after_user_change"]
            )

        with self.subTest(case="fresh-collision"):
            project = Path(self.temporary.name) / "late-fresh-collision"
            project.mkdir()
            target = project / ".agents/skills/research/SKILL.md"
            module = self.load_adopt(PACKAGE_ROOT, "late_fresh_collision_adopt")

            def create_collision() -> None:
                target.parent.mkdir(parents=True)
                target.write_bytes(b"late pre-existing skill bytes\n")

            assert_rejected(
                module,
                project,
                lambda: module.reconcile(
                    project, False, module.LOCAL_REVISION, "install"
                ),
                create_collision,
            )

        with self.subTest(case="composite"):
            project = Path(self.temporary.name) / "late-composite"
            project.mkdir()
            self.assert_ok(run_script(LIFECYCLE, "install", project))
            policy = project / "AGENTS.md"
            policy.write_bytes(
                policy.read_bytes().replace(b"MUST route every request", b"MUST maybe route every request")
            )
            module = self.load_adopt(PACKAGE_ROOT, "late_composite_adopt")
            assert_rejected(
                module,
                project,
                lambda: module.reconcile(
                    project, False, module.LOCAL_REVISION, "update"
                ),
                lambda: policy.write_bytes(b"late project policy bytes\n"),
            )

        with self.subTest(case="retirement"):
            project = Path(self.temporary.name) / "late-retirement"
            project.mkdir()
            self.assert_ok(run_script(LIFECYCLE, "install", project))
            target_name = ".agents/skills/tdd/tests.md"
            target = project / target_name
            package = self.package_without_mapping("late-retirement-package", target_name)
            module = self.load_adopt(package, "late_retirement_adopt")
            assert_rejected(
                module,
                project,
                lambda: module.reconcile(
                    project, False, module.LOCAL_REVISION, "update"
                ),
                lambda: target.write_bytes(b"late retirement edit\n"),
            )

        with self.subTest(case="remove"):
            project = Path(self.temporary.name) / "late-remove"
            project.mkdir()
            self.assert_ok(run_script(LIFECYCLE, "install", project))
            target = project / ".agents/skills/tdd/tests.md"
            module = self.load_adopt(PACKAGE_ROOT, "late_remove_adopt")
            assert_rejected(
                module,
                project,
                lambda: module.remove(project, False),
                lambda: target.write_bytes(b"late remove edit\n"),
            )

        with self.subTest(case="legacy"):
            project = Path(self.temporary.name) / "late-legacy"
            shutil.copytree(PINNED_FIXTURE / "project", project)
            target = project / ".agents/skills/setup-matt-pocock-skills/SKILL.md"
            module = self.load_adopt(PACKAGE_ROOT, "late_legacy_adopt")
            assert_rejected(
                module,
                project,
                lambda: module.reconcile(
                    project, False, module.LOCAL_REVISION, "update"
                ),
                lambda: target.write_bytes(b"late legacy edit\n"),
                "former skill root changed at lifecycle mutation boundary",
            )

    def test_atomic_capture_rejects_post_observation_and_post_proof_changes(self) -> None:
        with self.subTest(case="post-observation-write"):
            project = Path(self.temporary.name) / "post-observation-write"
            project.mkdir()
            self.assert_ok(run_script(LIFECYCLE, "install", project))
            target = project / ".agents/skills/research/SKILL.md"
            sibling = project / ".agents/skills/tdd/SKILL.md"
            target.write_bytes(b"stale target observed during planning\n")
            sibling.write_bytes(b"second stale target\n")
            before = stable_lifecycle_snapshot(project)
            late = b"late target bytes after atomic capture\n"
            module = self.load_adopt(PACKAGE_ROOT, "post_observation_adopt")
            original = module.exclusive_write
            injected = False

            def collide_after_capture(path, data, mode, root, created):
                nonlocal injected
                if path == target and not injected:
                    injected = True
                    path.write_bytes(late)
                return original(path, data, mode, root, created)

            with (
                mock.patch.object(module, "exclusive_write", collide_after_capture),
                self.assertRaises(module.AdoptionError) as raised,
            ):
                module.reconcile(project, False, module.LOCAL_REVISION, "update")
            self.assertIn("changed at lifecycle mutation boundary", str(raised.exception))
            self.assertEqual(target.read_bytes(), late)
            after = stable_lifecycle_snapshot(project)
            self.assertEqual(
                {path: value for path, value in after.items() if path != target.relative_to(project).as_posix()},
                {path: value for path, value in before.items() if path != target.relative_to(project).as_posix()},
            )
            self.assertFalse(list(project.glob(".agent-workflow-transaction-*")))

        with self.subTest(case="post-write-failure-replacement"):
            project = Path(self.temporary.name) / "post-write-failure-replacement"
            project.mkdir()
            self.assert_ok(run_script(LIFECYCLE, "install", project))
            target = project / ".agents/skills/research/SKILL.md"
            target.write_bytes(b"stale target observed during planning\n")
            before = stable_lifecycle_snapshot(project)
            late = b"authoritative replacement after the exclusive write\n"
            module = self.load_adopt(PACKAGE_ROOT, "post_write_failure_adopt")
            original_fsync = module.os.fsync
            injected = False

            def replace_then_fail(descriptor):
                nonlocal injected
                if not injected:
                    injected = True
                    replacement = target.with_name(".late-replacement")
                    replacement.write_bytes(late)
                    module.os.replace(replacement, target)
                    raise OSError("injected fsync failure")
                return original_fsync(descriptor)

            with (
                mock.patch.object(module.os, "fsync", replace_then_fail),
                self.assertRaises(OSError) as raised,
            ):
                module.reconcile(project, False, module.LOCAL_REVISION, "update")
            self.assertTrue(injected)
            self.assertIn("injected fsync failure", str(raised.exception))
            self.assertEqual(target.read_bytes(), late)
            relative = target.relative_to(project).as_posix()
            after = stable_lifecycle_snapshot(project)
            self.assertEqual(
                {path: value for path, value in after.items() if path != relative},
                {path: value for path, value in before.items() if path != relative},
            )
            self.assertFalse(list(project.glob(".agent-workflow-transaction-*")))

        proof_cases = {
            "skill-root": (
                ".agents/skills/setup-matt-pocock-skills/SKILL.md",
                "former skill root changed at lifecycle mutation boundary",
            ),
            "providers": (
                ".agent-workflow/providers.json",
                "former framework proof changed at lifecycle mutation boundary",
            ),
            "manifest": (
                ".agent-workflow/install-manifest.json",
                "former framework proof changed at lifecycle mutation boundary",
            ),
        }
        for case, (target_name, expected_error) in proof_cases.items():
            with self.subTest(case=f"post-legacy-proof-{case}"):
                project = Path(self.temporary.name) / f"post-legacy-proof-{case}"
                shutil.copytree(PINNED_FIXTURE / "project", project)
                target = project / target_name
                late = f"late {case} bytes after complete proof\n".encode()
                module = self.load_adopt(
                    PACKAGE_ROOT,
                    f"post_legacy_proof_{case.replace('-', '_')}_adopt",
                )
                original = module.prove_legacy_provider_installation
                proof_count = 0
                expected_after_change: dict[str, tuple[object, ...]] = {}

                def mutate_after_proof(root):
                    nonlocal proof_count, expected_after_change
                    original(root)
                    proof_count += 1
                    if proof_count == 2:
                        target.write_bytes(late)
                        expected_after_change = stable_lifecycle_snapshot(project)

                with (
                    mock.patch.object(
                        module,
                        "prove_legacy_provider_installation",
                        mutate_after_proof,
                    ),
                    self.assertRaises(module.AdoptionError) as raised,
                ):
                    module.reconcile(
                        project, False, module.LOCAL_REVISION, "update"
                    )
                self.assertEqual(proof_count, 2)
                self.assertIn(expected_error, str(raised.exception))
                self.assertEqual(
                    stable_lifecycle_snapshot(project), expected_after_change
                )
                for prefix in (
                    ".agent-workflow-transaction-*",
                    ".agent-workflow-backup-*",
                    ".agent-workflow-stage-*",
                ):
                    self.assertFalse(list(project.glob(prefix)))

        with self.subTest(case="post-framework-root-observation"):
            project = Path(self.temporary.name) / "post-framework-root-observation"
            shutil.copytree(PINNED_FIXTURE / "project", project)
            framework = project / ".agent-workflow"
            holder = project / ".late-framework-target"
            before = stable_lifecycle_snapshot(project)
            module = self.load_adopt(PACKAGE_ROOT, "post_framework_root_adopt")
            original_replace = module.os.replace
            injected = False
            expected_after_change: dict[str, tuple[object, ...]] = {}

            def replace_framework_with_symlink(source, destination):
                nonlocal injected, expected_after_change
                source_path = Path(source)
                destination_path = Path(destination)
                if (
                    source_path == framework
                    and destination_path.name.startswith(".agent-workflow-backup-")
                    and not injected
                ):
                    injected = True
                    original_replace(framework, holder)
                    framework.symlink_to(holder.name, target_is_directory=True)
                    expected_after_change = {
                        (
                            ".late-framework-target"
                            + path.removeprefix(".agent-workflow")
                            if path == ".agent-workflow"
                            or path.startswith(".agent-workflow/")
                            else path
                        ): value
                        for path, value in before.items()
                    }
                    symlink_stat = os.lstat(framework)
                    expected_after_change[".agent-workflow"] = (
                        "symlink",
                        stat.S_IMODE(symlink_stat.st_mode),
                        os.readlink(framework),
                    )
                return original_replace(source, destination)

            with (
                mock.patch.object(
                    module.os,
                    "replace",
                    replace_framework_with_symlink,
                ),
                self.assertRaises(module.AdoptionError) as raised,
            ):
                module.reconcile(project, False, module.LOCAL_REVISION, "update")
            self.assertTrue(injected)
            self.assertIn(
                ".agent-workflow changed type at lifecycle mutation boundary",
                str(raised.exception),
            )
            self.assertEqual(stable_lifecycle_snapshot(project), expected_after_change)
            for prefix in (
                ".agent-workflow-transaction-*",
                ".agent-workflow-backup-*",
                ".agent-workflow-stage-*",
            ):
                self.assertFalse(list(project.glob(prefix)))

    def test_fresh_install_remove_and_reinstall_is_complete(self) -> None:
        for command in ("install", "remove", "install"):
            with self.subTest(command=command):
                self.assert_ok(run_script(LIFECYCLE, command, self.project))
        self.assert_ok(run_script(LIFECYCLE, "status", self.project))
        self.assertEqual(
            {
                path.name
                for path in (self.project / ".agents/skills").iterdir()
                if path.is_dir()
            },
            RETAINED_SKILLS,
        )

    def test_transition_rolls_back_identically_at_both_failure_points(self) -> None:
        for point in ("after-external", "after-framework"):
            with self.subTest(point=point):
                project = Path(self.temporary.name) / f"rollback-{point}"
                shutil.copytree(PINNED_FIXTURE / "project", project)
                empty = project / ".agents/skills/project-local/empty/nested"
                empty.mkdir(parents=True)
                os.chmod(empty.parent, 0o750)
                before = lifecycle_snapshot(project)
                environment = os.environ.copy()
                environment["PYTHONDONTWRITEBYTECODE"] = "1"
                environment["AGENT_WORKFLOW_TEST_FAIL_AT"] = point

                result = run_script(
                    LIFECYCLE, "update", project, env=environment
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("injected lifecycle failure", result.stderr)
                self.assertEqual(lifecycle_snapshot(project), before)

    def test_fresh_install_and_retirement_roll_back_at_both_failure_points(self) -> None:
        retired = ".agents/skills/tdd/tests.md"
        for point in ("after-external", "after-framework"):
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["AGENT_WORKFLOW_TEST_FAIL_AT"] = point

            with self.subTest(point=point, case="fresh"):
                fresh = Path(self.temporary.name) / f"fresh-{point}"
                fresh.mkdir()
                before = lifecycle_snapshot(fresh)
                result = run_script(
                    LIFECYCLE, "install", fresh, env=environment
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(lifecycle_snapshot(fresh), before)

            with self.subTest(point=point, case="retirement"):
                project = Path(self.temporary.name) / f"retirement-rollback-{point}"
                project.mkdir()
                self.assert_ok(run_script(LIFECYCLE, "install", project))
                target = project / retired
                os.chmod(target, 0o600)
                before = lifecycle_snapshot(project)
                package = self.package_without_mapping(
                    f"retirement-rollback-package-{point}", retired
                )
                result = run_script(
                    package / "scripts/lifecycle.py",
                    "update",
                    project,
                    env=environment,
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(lifecycle_snapshot(project), before)

    def test_status_reports_every_update_only_manifest_or_directory_change(self) -> None:
        base = Path(self.temporary.name) / "status-parity-base"
        base.mkdir()
        self.assert_ok(run_script(LIFECYCLE, "install", base))

        for case in ("missing-entry", "retired-entry", "stale-digest", "empty-dir"):
            with self.subTest(case=case):
                project = Path(self.temporary.name) / f"status-parity-{case}"
                shutil.copytree(base, project)
                manifest_path = project / ".agent-workflow/install-manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                key = ".agents/skills/research/SKILL.md"
                if case == "missing-entry":
                    manifest["external_files"].pop(key)
                    manifest_path.write_bytes(manifest_bytes(manifest))
                elif case == "retired-entry":
                    manifest["external_files"][".agents/skills/retired/SKILL.md"] = {
                        "created": True,
                        "sha256": "0" * 64,
                    }
                    manifest_path.write_bytes(manifest_bytes(manifest))
                elif case == "stale-digest":
                    manifest["external_files"][key]["sha256"] = "0" * 64
                    manifest_path.write_bytes(manifest_bytes(manifest))
                else:
                    (project / ".agent-workflow/obsolete/empty").mkdir(parents=True)

                before = lifecycle_snapshot(project)
                status = run_script(LIFECYCLE, "status", project)
                self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
                self.assertIn("repairable", status.stdout)
                self.assertEqual(lifecycle_snapshot(project), before)
                self.assert_ok(run_script(LIFECYCLE, "update", project))
                healthy = run_script(LIFECYCLE, "status", project)
                self.assert_ok(healthy)
                self.assertIn("healthy", healthy.stdout)

    def test_idempotency_and_dry_run_leave_an_identical_snapshot(self) -> None:
        self.assert_ok(run_script(LIFECYCLE, "install", self.project))
        before = lifecycle_snapshot(self.project)

        dry_run = run_script(LIFECYCLE, "update", self.project, "--dry-run")
        self.assert_ok(dry_run)
        self.assertIn("UPDATE PLAN", dry_run.stdout)
        self.assertEqual(lifecycle_snapshot(self.project), before)

        self.assert_ok(run_script(LIFECYCLE, "update", self.project))
        self.assertEqual(lifecycle_snapshot(self.project), before)

    def test_cleanup_failure_is_a_warning_after_a_committed_transaction(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["AGENT_WORKFLOW_TEST_FAIL_AT"] = "cleanup-external"

        result = run_script(LIFECYCLE, "install", self.project, env=environment)

        self.assert_ok(result)
        self.assertIn("could not remove transaction backup", result.stderr)
        backups = list(self.project.glob(".agent-workflow-transaction-*"))
        self.assertEqual(len(backups), 1)
        status = run_script(LIFECYCLE, "status", self.project)
        self.assert_ok(status)
        self.assertIn("healthy", status.stdout)
        shutil.rmtree(backups[0])

    def test_unsafe_framework_or_durable_entries_block_every_mutation(self) -> None:
        base = Path(self.temporary.name) / "unsafe-preflight-base"
        base.mkdir()
        self.assert_ok(run_script(LIFECYCLE, "install", base))

        for case in ("framework-symlink", "framework-special", "durable-symlink"):
            with self.subTest(case=case):
                project = Path(self.temporary.name) / case
                shutil.copytree(base, project)
                if case == "framework-symlink":
                    (project / ".agent-workflow/unsafe").symlink_to("README.md")
                elif case == "framework-special":
                    os.mkfifo(project / ".agent-workflow/unsafe")
                else:
                    durable = project / ".agent-wayfinder"
                    durable.rmdir()
                    outside = Path(self.temporary.name) / f"outside-{case}"
                    outside.mkdir()
                    durable.symlink_to(outside, target_is_directory=True)

                before = lifecycle_snapshot(project)
                for command in ("status", "install", "update", "remove"):
                    result = run_script(LIFECYCLE, command, project)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("CONFLICT" if command == "status" else "ERROR", result.stdout + result.stderr)
                    self.assertEqual(lifecycle_snapshot(project), before)


if __name__ == "__main__":
    import unittest

    unittest.main()
