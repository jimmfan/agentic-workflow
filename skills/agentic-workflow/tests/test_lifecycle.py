from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from typing import Optional


PACKAGE = Path(__file__).resolve().parent.parent
ADOPT = PACKAGE / "scripts" / "adopt.py"
BOOTSTRAP = PACKAGE / "scripts" / "bootstrap.py"
VERIFY = PACKAGE / "scripts" / "verify_package.py"
REVISION = "1" * 40


def run(*args: object, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
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
        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("Installation is clean", status.stdout)

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
        target = git_repository(self.base / "target")
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
            target,
            "--archive-url",
            archive.as_uri(),
            "--ref",
            REVISION,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("installed and verified", result.stdout)
        installed = json.loads((target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(installed["source_revision"], REVISION)


if __name__ == "__main__":
    unittest.main()
