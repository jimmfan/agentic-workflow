"""Offline controls for immutable consumers, historical layouts, and skill mixes."""

import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from evals.campaign import revisions


INSTALLER = """from pathlib import Path
import json, sys
source = Path(__file__).resolve().parent.parent
target = Path(sys.argv[2])
manifest = json.loads((source / "agent_workflow/install/manifest.json").read_text())
for item in manifest["framework_owned"]:
    path = target / item["target"]
    data = (source / item["source"]).read_bytes()
    if sys.argv[1] == "install":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    elif not path.is_file() or path.read_bytes() != data:
        raise SystemExit(1)
"""


class RevisionPreparationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic Evaluation")
        self.git("config", "user.email", "synthetic@example.invalid")
        self.base_files = {
            "AGENTS.md": "Frozen consumer policy\n",
            ".agent-workflow/contracts/base.md": "Base contract\n",
            ".agents/skills/sample/SKILL.md": "# Sample\nRead [old helper](old.md).\n",
            ".agents/skills/sample/old.md": "old helper\n",
        }
        self.base = self.commit_files(self.base_files, "0.30.0")
        self.destination = self.root / "consumer"

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), *args], stderr=subprocess.PIPE, text=True
        ).strip()

    def commit_files(self, files, version):
        for directory in (".agent-workflow", ".agents", "agent_workflow"):
            shutil.rmtree(self.repo / directory, ignore_errors=True)
        script = self.repo / "agent_workflow/lifecycle.py"
        script.parent.mkdir()
        script.write_text(INSTALLER)
        mappings = []
        for target, value in files.items():
            source = (
                "agent_workflow/install/AGENTS.md.template"
                if target == "AGENTS.md"
                else target
            )
            path = self.repo / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
            mappings.append({"source": source, "target": target})
        (self.repo / "agent_workflow/install/manifest.json").write_text(
            json.dumps({"framework_owned": mappings})
        )
        (self.repo / "VERSION").write_text(version + "\n")
        self.git("add", "-A")
        self.git("commit", "-qm", f"Synthetic fixture {version}")
        return self.git("rev-parse", "HEAD")

    def test_frozen_commit_ignores_worktree_and_preserves_source(self):
        source = self.repo / ".agents/skills/sample/SKILL.md"
        source.write_text("Uncommitted author work\n")
        status = self.git("status", "--porcelain")
        metadata = revisions.prepare_revision(self.repo, self.base, self.destination)
        self.assertEqual(metadata["commit"], self.base)
        self.assertEqual(
            (self.destination / ".agents/skills/sample/SKILL.md").read_text(),
            self.base_files[".agents/skills/sample/SKILL.md"],
        )
        self.assertEqual(source.read_text(), "Uncommitted author work\n")
        self.assertEqual(self.git("status", "--porcelain"), status)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        revisions.verify_files(self.destination, metadata["files"])

    def test_whole_skill_replacement_removes_stale_files_and_keeps_provenance(self):
        files = {
            key: value
            for key, value in self.base_files.items()
            if not key.endswith("old.md")
        }
        files[".agents/skills/sample/SKILL.md"] = "# Sample\nRead [helper](new.md).\n"
        files[".agents/skills/sample/new.md"] = "new helper\n"
        files[".agents/skills/sample/agents/openai.yaml"] = (
            "policy:\n  allow_implicit_invocation: false\n"
        )
        donor = self.commit_files(files, "0.31.0")
        metadata = revisions.prepare_revision(
            self.repo,
            self.base,
            self.destination,
            overlays=[{"skill": "sample", "ref": donor}],
        )
        skill = self.destination / ".agents/skills/sample"
        self.assertFalse((skill / "old.md").exists())
        self.assertTrue((skill / "new.md").is_file())
        self.assertTrue((skill / "agents/openai.yaml").is_file())
        overlay = metadata["overlays"][0]
        self.assertEqual(
            (overlay["base_commit"], overlay["donor_commit"]), (self.base, donor)
        )
        self.assertIn("old.md", overlay["before_files"])
        self.assertNotIn("old.md", overlay["files"])

    def test_missing_framework_dependency_rejects_mix_atomically(self):
        files = {
            **self.base_files,
            ".agent-workflow/contracts/new.md": "New contract\n",
        }
        files[".agents/skills/sample/SKILL.md"] = (
            "Read `.agent-workflow/contracts/new.md`.\n"
        )
        donor = self.commit_files(files, "0.31.0")
        with self.assertRaisesRegex(ValueError, "missing local dependencies.*new.md"):
            revisions.prepare_revision(
                self.repo,
                self.base,
                self.destination,
                overlays=[{"skill": "sample", "ref": donor}],
            )
        self.assertFalse(self.destination.exists())

    def test_invalid_refs_and_overlay_path_escape(self):
        for ref in ("", "--help", "does-not-exist"):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                revisions.prepare_revision(self.repo, ref, self.destination)
        for skill in ("../../escape", "/tmp/escape", "sample/child"):
            with (
                self.subTest(skill=skill),
                self.assertRaisesRegex(ValueError, "simple skill name"),
            ):
                revisions.prepare_revision(
                    self.repo,
                    self.base,
                    self.destination,
                    overlays=[{"skill": skill, "ref": self.base}],
                )
        self.assertFalse(self.destination.exists())

    def test_existing_destination_and_source_overlap_are_rejected(self):
        self.destination.mkdir()
        sentinel = self.destination / "keep.txt"
        sentinel.write_text("user-owned\n")
        with self.assertRaisesRegex(ValueError, "must not exist"):
            revisions.prepare_revision(self.repo, self.base, self.destination)
        with self.assertRaisesRegex(ValueError, "overlaps source"):
            revisions.prepare_revision(self.repo, self.base, self.repo / "new-consumer")
        self.assertEqual(sentinel.read_text(), "user-owned\n")

    def test_source_overlap_through_symlink_parent_is_rejected(self):
        link = self.root / "alias"
        link.symlink_to(self.repo, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "overlaps source"):
            revisions.prepare_revision(self.repo, self.base, link / "escaped-consumer")

    def test_documented_artifacts_subtree_is_allowed(self):
        parent = self.repo / "evals/artifacts/test/payloads"
        parent.mkdir(parents=True)
        metadata = revisions.prepare_revision(self.repo, self.base, parent / "base")
        self.assertEqual(metadata["commit"], self.base)

    def test_payload_drift_is_detected(self):
        metadata = revisions.prepare_revision(self.repo, self.base, self.destination)
        (self.destination / "AGENTS.md").write_text("Changed instruction\n")
        with self.assertRaisesRegex(ValueError, "payload drift: AGENTS.md"):
            revisions.verify_files(self.destination, metadata["files"])

    def test_escaping_archive_member_is_rejected(self):
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w") as bundle:
            entry = tarfile.TarInfo("../escaped.txt")
            entry.size = 4
            bundle.addfile(entry, io.BytesIO(b"oops"))
        original = revisions._git

        def git(repo, *args):
            return archive.getvalue() if args[0] == "archive" else original(repo, *args)

        with (
            patch.object(revisions, "_git", side_effect=git),
            self.assertRaisesRegex(ValueError, "unsafe Git archive"),
        ):
            revisions.prepare_revision(self.repo, self.base, self.destination)
        self.assertFalse((self.root / "escaped.txt").exists())
        self.assertFalse(self.destination.exists())

    def test_legacy_optional_provider_failure_is_not_accepted_as_core_success(self):
        shutil.rmtree(self.repo / "agent_workflow")
        package = self.repo / "skills/agent-workflow"
        (package / "scripts").mkdir(parents=True)
        (package / "payload/distribution").mkdir(parents=True)
        (package / "VERSION").write_text("0.20.0\n")
        (package / "payload/distribution/manifest.json").write_text(
            '{"framework_version":"0.20.0"}'
        )
        (package / "scripts/lifecycle.py").write_text("raise SystemExit(0)\n")
        (package / "scripts/providers.py").write_text(
            "print('provider projection incomplete')\nraise SystemExit(1)\n"
        )
        self.git("add", "-A")
        self.git("commit", "-qm", "Synthetic optional provider failure")
        with self.assertRaisesRegex(RuntimeError, "provider projection incomplete"):
            revisions.prepare_revision(self.repo, "HEAD", self.destination)
        self.assertFalse(self.destination.exists())

    def test_escaping_installed_symlink_is_rejected(self):
        self.destination.mkdir()
        (self.destination / "leak").symlink_to(self.repo / "VERSION")
        with self.assertRaisesRegex(ValueError, "symlink escapes"):
            revisions.snapshot_files(self.destination)


class HistoricalSourceSmokeTests(unittest.TestCase):
    def test_known_actual_revisions_prepare_offline(self):
        repo = Path(__file__).resolve().parents[2]
        candidates = (
            ("7a181d2b200e25d113591abe774a7a88f6a70089", "0.20.0", "legacy-payload"),
            ("4589dc7d1c35fe49cf4ef943a92f64520b9f968a", "0.30.0", "canonical-source"),
            ("deb91942ac45373111a6bc615b359b2bbb230a68", "0.41.2", "canonical-source"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            for index, (commit, version, layout) in enumerate(candidates):
                with self.subTest(version=version):
                    try:
                        revisions.resolve_revision(repo, commit)
                    except ValueError:
                        self.skipTest(f"historical Git object unavailable: {commit}")
                    destination = Path(temporary) / str(index)
                    metadata = revisions.prepare_revision(repo, commit, destination)
                    self.assertEqual(
                        (metadata["version"], metadata["layout"]), (version, layout)
                    )
                    revisions.verify_files(destination, metadata["files"])
                    if version == "0.20.0":
                        self.assertTrue(
                            any("0.19.1" in item for item in metadata["warnings"])
                        )


class FrozenInventoryTests(unittest.TestCase):
    def test_copy_preserves_complete_inventory_including_empty_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "original"
            root.mkdir()
            root.chmod(0o750)
            (root / "empty").mkdir()
            (root / "empty").chmod(0o700)
            (root / "script").write_text("pass\n")
            (root / "script").chmod(0o755)
            (root / "alias").symlink_to("script")
            expected = revisions.snapshot_files(root)
            self.assertEqual(expected["."], {"kind": "directory", "mode": 0o750})
            self.assertEqual(expected["empty"], {"kind": "directory", "mode": 0o700})
            self.assertEqual(expected["script"]["mode"], 0o755)
            self.assertEqual(expected["alias"], {"kind": "symlink", "target": "script"})
            copied = Path(temporary) / "copy"
            shutil.copytree(root, copied, symlinks=True)
            revisions.verify_files(copied, expected)
            (copied / "empty").rmdir()
            with self.assertRaisesRegex(ValueError, "payload drift: empty"):
                revisions.verify_files(copied, expected)

    def test_content_only_inventory_is_rejected_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "note.txt").write_bytes(b"")
            expected = {
                "note.txt": {
                    "kind": "file",
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                }
            }
            original = json.dumps(expected)
            with self.assertRaisesRegex(ValueError, "payload drift"):
                revisions.verify_files(root, expected)
            self.assertEqual(json.dumps(expected), original)


if __name__ == "__main__":
    unittest.main()
