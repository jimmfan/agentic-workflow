from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
from typing import Mapping, Optional


PACKAGE = Path(__file__).resolve().parent.parent
ADOPT = PACKAGE / "scripts" / "adopt.py"
BOOTSTRAP = PACKAGE / "scripts" / "bootstrap.py"
VERIFY = PACKAGE / "scripts" / "verify_package.py"
REVISION = "1" * 40
FORMER_FRAMEWORK_DOCS = (
    "docs/architecture.md",
    "docs/decisions/0002-use-checksummed-copy-adoption.md",
    "docs/decisions/0003-use-internal-reference-inspired-workflows.md",
    "docs/decisions/0005-add-decomposition-and-independent-review.md",
    "docs/decisions/0006-use-inert-bootstrap-payload.md",
    "docs/routing.md",
    "docs/verification.md",
)


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load test module from {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


ADOPTER = load_script("agentic_workflow_adopt", ADOPT)
BOOTSTRAPPER = load_script("agentic_workflow_bootstrap", BOOTSTRAP)
VERIFIER = load_script("agentic_workflow_verify", VERIFY)


def run(
    *args: object,
    cwd: Optional[Path] = None,
    env: Optional[Mapping[str, str]] = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def git_repository(root: Path) -> Path:
    root.mkdir(parents=True)
    result = run("git", "init", "-q", str(root))
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return root


def adopt(script: Path, action: str, target: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return run(sys.executable, script, action, target, "--source-revision", REVISION, *extra)


class LifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="agentic-workflow-test-")
        self.base = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_fresh_install_is_one_operation_and_verified(self) -> None:
        target = git_repository(self.base / "target")
        result = adopt(ADOPT, "install", target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("installed and verified", result.stdout)
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertTrue((target / ".agents/skills/workflow-teach/SKILL.md").is_file())
        self.assertTrue((target / "ai-workflow/project-profile.md").is_file())
        self.assertTrue((target / "ai-workflow/state/active.md").is_file())
        self.assertFalse((target / "docs").exists())
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertFalse((target / relative).exists())
        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("Installation is clean", status.stdout)

    def test_non_git_install_update_status_and_remove(self) -> None:
        target = self.base / "ordinary-project"
        target.mkdir()
        self.assertFalse((target / ".git").exists())

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)
        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())
        self.assertTrue((target / "ai-workflow/project-profile.md").is_file())

    def test_target_project_docs_are_never_supplied_or_removed(self) -> None:
        target = self.base / "documented-project"
        project_decision = target / "docs/decisions/0001-project-architecture.md"
        project_decision.parent.mkdir(parents=True)
        project_decision.write_text("# Project-owned decision\n", encoding="utf-8")

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(project_decision.read_text(encoding="utf-8"), "# Project-owned decision\n")
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertFalse((target / relative).exists())

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(project_decision.read_text(encoding="utf-8"), "# Project-owned decision\n")

    def test_default_target_is_current_directory(self) -> None:
        target = self.base / "current-project"
        target.mkdir()
        result = run(
            sys.executable,
            ADOPT,
            "install",
            "--source-revision",
            REVISION,
            cwd=target,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "ai-workflow/install-manifest.json").is_file())

    def test_explicit_target_is_used_from_another_directory(self) -> None:
        working = self.base / "working"
        target = self.base / "explicit-project"
        working.mkdir()
        target.mkdir()
        result = run(
            sys.executable,
            ADOPT,
            "install",
            target,
            "--source-revision",
            REVISION,
            cwd=working,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "ai-workflow/install-manifest.json").is_file())
        self.assertFalse((working / "ai-workflow").exists())

    def test_install_does_not_need_git_executable(self) -> None:
        target = self.base / "no-git-project"
        target.mkdir()
        environment = os.environ.copy()
        environment["PATH"] = str(self.base / "no-executables")
        result = run(
            sys.executable,
            ADOPT,
            "install",
            target,
            "--source-revision",
            REVISION,
            env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "ai-workflow/install-manifest.json").is_file())

    def test_filesystem_root_is_rejected(self) -> None:
        root = Path(Path.cwd().anchor)
        result = adopt(ADOPT, "install", root)
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to operate on a filesystem root", result.stderr)
        with self.assertRaisesRegex(BOOTSTRAPPER.BootstrapError, "filesystem root"):
            BOOTSTRAPPER.main(
                [
                    "install",
                    str(root),
                    "--archive-url",
                    (self.base / "unused.tar.gz").as_uri(),
                    "--ref",
                    REVISION,
                ]
            )

    def test_dry_run_is_optional_and_nonmutating(self) -> None:
        target = git_repository(self.base / "target")
        result = adopt(ADOPT, "install", target, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())

    def test_existing_policy_is_preserved_through_install_and_remove(self) -> None:
        target = git_repository(self.base / "target")
        original = b"# Project policy\n\nKeep this exact content.\n"
        (target / "AGENTS.md").write_bytes(original)
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        composite = (target / "AGENTS.md").read_bytes()
        self.assertIn(original, composite)
        profile = target / "ai-workflow/project-profile.md"
        profile.write_text("project-owned customization\n", encoding="utf-8")
        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual((target / "AGENTS.md").read_bytes(), original)
        self.assertEqual(profile.read_text(encoding="utf-8"), "project-owned customization\n")
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())

    def test_conflict_fails_before_writes(self) -> None:
        target = git_repository(self.base / "target")
        conflict = target / ".agents/skills/workflow-teach/SKILL.md"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("project owned\n", encoding="utf-8")
        result = adopt(ADOPT, "install", target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("would overwrite existing framework path", result.stderr)
        self.assertEqual(conflict.read_text(encoding="utf-8"), "project owned\n")
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())

    def test_reinstallation_is_idempotent(self) -> None:
        target = git_repository(self.base / "target")
        first = adopt(ADOPT, "install", target)
        self.assertEqual(first.returncode, 0, first.stderr)
        manifest = (target / "ai-workflow/install-manifest.json").read_bytes()
        second = adopt(ADOPT, "install", target)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already installed and verified", second.stdout)
        self.assertEqual((target / "ai-workflow/install-manifest.json").read_bytes(), manifest)

    def test_tamper_is_reported_and_blocks_update(self) -> None:
        target = git_repository(self.base / "target")
        self.assertEqual(adopt(ADOPT, "install", target).returncode, 0)
        skill = target / ".agents/skills/workflow-teach/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal change\n", encoding="utf-8")
        self.assertEqual(adopt(ADOPT, "status", target).returncode, 1)
        update = adopt(ADOPT, "update", target)
        self.assertEqual(update.returncode, 2)
        self.assertIn("locally changed framework file", update.stderr)

    def test_installation_manifest_cannot_hide_file_tampering(self) -> None:
        target = git_repository(self.base / "target")
        self.assertEqual(adopt(ADOPT, "install", target).returncode, 0)
        relative = ".agents/skills/workflow-teach/SKILL.md"
        skill = target / relative
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal change\n", encoding="utf-8")
        digest = hashlib.sha256(skill.read_bytes()).hexdigest()
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_files"][relative]["sha256"] = digest
        manifest["framework_files"][relative]["source_sha256"] = digest
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 2)
        self.assertIn("source checksum was changed", status.stderr)

    def test_update_preserves_project_owned_content_and_removes_allowlisted_retirement(self) -> None:
        old_package = self.base / "old-package"
        shutil.copytree(PACKAGE, old_package)
        (old_package / "VERSION").write_text("0.3.0\n", encoding="utf-8")
        refreshed = run(sys.executable, old_package / "scripts/verify_package.py", "--refresh-manifest")
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)

        manifest_path = old_package / "payload/distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        retired_source = manifest["retired_framework_owned"][-1]
        legacy = old_package / "payload" / retired_source
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text("legacy framework file\n", encoding="utf-8")
        manifest["retired_framework_owned"].remove(retired_source)
        manifest["framework_owned"].append({"source": retired_source, "target": retired_source})
        manifest["framework_owned"].sort(key=lambda item: item["source"])
        manifest["checksums"][retired_source] = hashlib.sha256(legacy.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        target = git_repository(self.base / "target")
        old_install = adopt(old_package / "scripts/adopt.py", "install", target)
        self.assertEqual(old_install.returncode, 0, old_install.stderr)
        profile = target / "ai-workflow/project-profile.md"
        profile.write_text("custom project profile\n", encoding="utf-8")
        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual(profile.read_text(encoding="utf-8"), "custom project profile\n")
        self.assertFalse((target / retired_source).exists())

    def test_update_removes_all_unchanged_framework_docs_from_legacy_install(self) -> None:
        old_package = self.base / "legacy-docs-package"
        shutil.copytree(PACKAGE, old_package)
        (old_package / "VERSION").write_text("0.4.0\n", encoding="utf-8")
        refreshed = run(sys.executable, old_package / "scripts/verify_package.py", "--refresh-manifest")
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)

        manifest_path = old_package / "payload/distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for relative in FORMER_FRAMEWORK_DOCS:
            destination = old_package / "payload" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(f"# Legacy framework documentation\n\n{relative}\n", encoding="utf-8")
            manifest["retired_framework_owned"].remove(relative)
            manifest["framework_owned"].append({"source": relative, "target": relative})
            manifest["checksums"][relative] = hashlib.sha256(destination.read_bytes()).hexdigest()
        manifest["framework_owned"].sort(key=lambda item: item["source"])
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        target = self.base / "legacy-target"
        target.mkdir()
        old_install = adopt(old_package / "scripts/adopt.py", "install", target)
        self.assertEqual(old_install.returncode, 0, old_install.stderr)
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertTrue((target / relative).is_file())

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertFalse((target / "docs").exists())
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertFalse((target / relative).exists())

    def test_package_version_and_checksum_drift_are_detected(self) -> None:
        copied = self.base / "package"
        shutil.copytree(PACKAGE, copied)
        (copied / "payload/VERSION").write_text("9.9.9\n", encoding="utf-8")
        mismatch = run(sys.executable, copied / "scripts/verify_package.py")
        self.assertEqual(mismatch.returncode, 1)
        self.assertIn("payload VERSION", mismatch.stderr)

        shutil.rmtree(copied)
        shutil.copytree(PACKAGE, copied)
        policy = copied / "payload/root/AGENTS.md.template"
        policy.write_text(policy.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
        checksum = run(sys.executable, copied / "scripts/verify_package.py")
        self.assertEqual(checksum.returncode, 1)
        self.assertIn("manifest/version/checksums drifted", checksum.stderr)

    def test_package_is_path_independent(self) -> None:
        copied = self.base / "nested/location/agentic-workflow"
        shutil.copytree(PACKAGE, copied)
        verified = run(sys.executable, copied / "scripts/verify_package.py")
        self.assertEqual(verified.returncode, 0, verified.stderr)
        target = git_repository(self.base / "target")
        installed = adopt(copied / "scripts/adopt.py", "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

    def test_bootstrap_download_fixture_installs_in_one_invocation(self) -> None:
        archive = self.base / "package.tar.gz"
        with tarfile.open(archive, "w:gz") as opened:
            opened.add(PACKAGE, arcname="source/skills/agentic-workflow")
        target = self.base / "target"
        target.mkdir()
        loader = (
            "from urllib.request import urlopen; "
            f"exec(compile(urlopen({BOOTSTRAP.as_uri()!r}, timeout=30).read(), "
            "'agentic-workflow-bootstrap.py', 'exec'))"
        )
        environment = os.environ.copy()
        environment["PATH"] = str(self.base / "no-executables")
        result = run(
            sys.executable,
            "-c",
            loader,
            "install",
            target,
            "--archive-url",
            archive.as_uri(),
            "--ref",
            REVISION,
            env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("installed and verified", result.stdout)
        installed = json.loads((target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(installed["source_revision"], REVISION)

    def test_bootstrap_defaults_to_current_project_directory(self) -> None:
        archive = self.base / "package.tar.gz"
        with tarfile.open(archive, "w:gz") as opened:
            opened.add(PACKAGE, arcname="source/skills/agentic-workflow")
        target = self.base / "current-bootstrap-project"
        target.mkdir()
        loader = (
            "from urllib.request import urlopen; "
            f"exec(compile(urlopen({BOOTSTRAP.as_uri()!r}, timeout=30).read(), "
            "'agentic-workflow-bootstrap.py', 'exec'))"
        )
        result = run(
            sys.executable,
            "-c",
            loader,
            "install",
            "--archive-url",
            archive.as_uri(),
            "--ref",
            REVISION,
            cwd=target,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "ai-workflow/install-manifest.json").is_file())

    def test_windows_ordinary_modes_are_canonicalized(self) -> None:
        source = self.base / "downloaded.md"
        source.write_text("ordinary payload\n", encoding="utf-8")
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o666):
            mode = ADOPTER.reviewed_source_mode(
                source, "simulated Windows source", posix_modes_meaningful=False
            )
        self.assertEqual(mode, 0o644)
        with mock.patch.object(VERIFIER.stat, "S_IMODE", return_value=0o666):
            mode = VERIFIER.reviewed_filesystem_mode(
                source,
                expected=0o644,
                posix_modes_meaningful=False,
            )
        self.assertEqual(mode, 0o644)

    def test_windows_mode_validation_is_bounded(self) -> None:
        source = self.base / "downloaded.md"
        source.write_text("ordinary payload\n", encoding="utf-8")
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o600):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "ordinary Windows file mode"):
                ADOPTER.reviewed_source_mode(
                    source, "simulated Windows source", posix_modes_meaningful=False
                )

    def test_posix_modes_remain_strict_and_preserve_executable_intent(self) -> None:
        source = self.base / "source"
        source.write_text("payload\n", encoding="utf-8")
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o644):
            self.assertEqual(
                ADOPTER.reviewed_source_mode(source, "POSIX data", posix_modes_meaningful=True),
                0o644,
            )
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o755):
            self.assertEqual(
                ADOPTER.reviewed_source_mode(
                    source,
                    "POSIX script",
                    expected_mode=0o755,
                    posix_modes_meaningful=True,
                ),
                0o755,
            )
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o755):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "mode must be 0644"):
                ADOPTER.reviewed_source_mode(
                    source, "POSIX data", posix_modes_meaningful=True
                )
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o4755):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "mode must be 0644"):
                ADOPTER.reviewed_source_mode(source, "privileged POSIX source", posix_modes_meaningful=True)
        with mock.patch.object(VERIFIER.stat, "S_IMODE", return_value=0o4755):
            with self.assertRaisesRegex(VERIFIER.VerificationError, "mode must be 0644"):
                VERIFIER.reviewed_filesystem_mode(
                    source,
                    expected=0o644,
                    posix_modes_meaningful=True,
                )

    def test_archive_rejects_privileged_file_mode_before_extraction(self) -> None:
        archive = io.BytesIO()
        data = b"payload\n"
        with tarfile.open(fileobj=archive, mode="w:gz") as opened:
            member = tarfile.TarInfo("source/skills/agentic-workflow/payload/file.md")
            member.mode = 0o4644
            member.size = len(data)
            opened.addfile(member, io.BytesIO(data))
        (self.base / "extracted").mkdir()
        with self.assertRaisesRegex(BOOTSTRAPPER.BootstrapError, "archive package file mode"):
            BOOTSTRAPPER.extract_package(archive.getvalue(), self.base / "extracted")

    def test_archive_accepts_git_mode_variant_and_canonicalizes_it(self) -> None:
        archive = io.BytesIO()
        data = b"payload\n"
        with tarfile.open(fileobj=archive, mode="w:gz") as opened:
            member = tarfile.TarInfo("source/skills/agentic-workflow/payload/file.md")
            member.mode = 0o664
            member.size = len(data)
            opened.addfile(member, io.BytesIO(data))
        destination = self.base / "git-archive"
        destination.mkdir()
        package = BOOTSTRAPPER.extract_package(archive.getvalue(), destination)
        extracted = package / "payload/file.md"
        self.assertEqual(extracted.read_bytes(), data)
        self.assertEqual(ADOPTER.reviewed_source_mode(extracted, "extracted Git archive file"), 0o644)


if __name__ == "__main__":
    unittest.main()
