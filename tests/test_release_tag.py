from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RELEASE_SCRIPT = REPOSITORY_ROOT / ".github" / "scripts" / "release_tag.py"
WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "verify.yml"


class ReleaseRepository:
    def __init__(self, root: Path) -> None:
        self.work = root / "work"
        self.remote = root / "origin.git"
        self.work.mkdir()
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Release Test")
        self.git("config", "user.email", "release-test@example.invalid")
        self.git("init", "--bare", str(self.remote), cwd=root)
        self.git("remote", "add", "origin", str(self.remote))
        self.write_version("0.19.1")
        self.before = self.commit("Initial version")

    def git(
        self,
        *args: str,
        cwd: Path | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=cwd or self.work,
            capture_output=True,
            text=True,
            check=check,
        )

    def write_version(self, version: str) -> None:
        path = self.work / "VERSION"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(version + "\n", encoding="utf-8")

    def commit(self, message: str) -> str:
        self.git("add", ".")
        self.git("commit", "--message", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def commit_version(self, version: str) -> str:
        self.write_version(version)
        return self.commit(f"Set version to {version}")

    def commit_without_version_change(self) -> str:
        (self.work / "README.md").write_text("ordinary change\n", encoding="utf-8")
        return self.commit("Ordinary change")

    def create_tag(self, tag: str, commit: str | None = None) -> None:
        self.git("tag", "--annotate", "--message", tag, tag, commit or self.before)

    def run_release(
        self, commit: str, *, publish: bool = True
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                str(RELEASE_SCRIPT),
                "--base",
                self.before,
                "--head",
                commit,
                *(["--publish"] if publish else []),
            ],
            cwd=self.work,
            env=environment,
            capture_output=True,
            text=True,
        )


class ReleaseTagPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = ReleaseRepository(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_validation_never_writes_local_or_remote_tags(self):
        commit = self.repository.commit_version("0.20.0")
        before = self.repository.git("show-ref", check=False).stdout
        result = self.repository.run_release(commit, publish=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(before, self.repository.git("show-ref", check=False).stdout)
        self.assertEqual(
            self.repository.git("ls-remote", "--tags", "origin").stdout, ""
        )

    def test_published_annotated_tag_is_a_successful_retry(self):
        commit = self.repository.commit_version("0.20.0")
        self.assertEqual(self.repository.run_release(commit).returncode, 0)
        remote = self.repository.git("ls-remote", "--tags", "origin").stdout
        self.repository.git("tag", "--delete", "v0.20.0")
        result = self.repository.run_release(commit)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("already published", result.stdout)
        self.assertEqual(
            remote, self.repository.git("ls-remote", "--tags", "origin").stdout
        )

    def test_failed_push_leaves_local_tag_pending_and_retry_publishes_it(self):
        commit = self.repository.commit_version("0.20.0")
        hook = self.repository.remote / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        failed = self.repository.run_release(commit)
        self.assertNotEqual(failed.returncode, 0)
        self.assertTrue(self.repository.git("tag", "--list").stdout)
        validation = self.repository.run_release(commit, publish=False)
        self.assertEqual(validation.returncode, 0, validation.stdout)
        self.assertNotIn("already published", validation.stdout)
        self.assertEqual(
            self.repository.git("ls-remote", "--tags", "origin").stdout, ""
        )
        hook.unlink()
        self.assertEqual(self.repository.run_release(commit).returncode, 0)
        self.assertIn(
            "refs/tags/v0.20.0^{}",
            self.repository.git("ls-remote", "--tags", "origin").stdout,
        )

    def test_remote_lightweight_or_wrong_commit_tag_conflicts(self):
        commit = self.repository.commit_version("0.20.0")
        self.repository.git("tag", "v0.20.0", commit)
        self.repository.git("push", "origin", "refs/tags/v0.20.0")
        self.repository.git("tag", "--delete", "v0.20.0")
        result = self.repository.run_release(commit, publish=False)
        self.assertNotEqual(result.returncode, 0)

    def test_remote_annotated_tag_at_another_commit_is_not_moved(self):
        self.repository.create_tag("v0.20.0")
        self.repository.git("push", "origin", "refs/tags/v0.20.0")
        self.repository.git("tag", "--delete", "v0.20.0")
        remote = self.repository.git("ls-remote", "--tags", "origin").stdout
        commit = self.repository.commit_version("0.20.0")
        for publish in (False, True):
            result = self.repository.run_release(commit, publish=publish)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("conflicting", result.stdout)
        self.assertEqual(
            remote, self.repository.git("ls-remote", "--tags", "origin").stdout
        )

    def test_base_version_must_increase_even_without_tags(self):
        for version in ("0.19.0", "00.20.0", "0.020.0", "0.20.0-rc1"):
            commit = self.repository.commit_version(version)
            self.assertNotEqual(
                self.repository.run_release(commit, publish=False).returncode,
                0,
                version,
            )

    def test_unchanged_version_does_not_request_a_release(self) -> None:
        commit = self.repository.commit_without_version_change()

        result = self.repository.run_release(commit)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no release tag requested", result.stdout)
        self.assertEqual(self.repository.git("tag", "--list").stdout, "")

    def test_lower_version_is_rejected(self) -> None:
        self.repository.create_tag("v0.20.0")
        commit = self.repository.commit_version("0.19.9")

        result = self.repository.run_release(commit)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "must be greater than highest release tag v0.20.0",
            result.stdout,
        )

    def test_existing_tag_reuse_is_rejected(self) -> None:
        self.repository.create_tag("v0.20.0")
        commit = self.repository.commit_version("0.20.0")

        result = self.repository.run_release(commit)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stdout)

    def test_malformed_version_is_rejected(self) -> None:
        commit = self.repository.commit_version("0.20")

        result = self.repository.run_release(commit)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must use x.y.z", result.stdout)

    def test_annotated_tag_targets_the_exact_triggering_commit(self) -> None:
        commit = self.repository.commit_version("0.20.0")
        self.repository.commit_without_version_change()

        result = self.repository.run_release(commit)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Created annotated v0.20.0", result.stdout)
        tag_object_type = self.repository.git(
            "cat-file", "-t", "v0.20.0"
        ).stdout.strip()
        target = self.repository.git("rev-parse", "v0.20.0^{}").stdout.strip()
        remote_target = self.repository.git(
            "--git-dir",
            str(self.repository.remote),
            "rev-parse",
            "v0.20.0^{}",
        ).stdout.strip()
        self.assertEqual(tag_object_type, "tag")
        self.assertEqual(target, commit)
        self.assertEqual(remote_target, commit)


class ReleaseWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.verify_job, cls.release_job = cls.workflow.split(
            "\n  release-tag:\n", maxsplit=1
        )

    def test_tagging_job_requires_successful_verification(self) -> None:
        self.assertIn(
            "needs: [deterministic-pre-merge-gate, stable-python, macos-lifecycle]",
            self.release_job,
        )
        self.assertIn("github.event_name == 'push'", self.release_job)
        self.assertIn("github.ref == 'refs/heads/main'", self.release_job)

    def test_only_tagging_job_receives_write_permission(self) -> None:
        self.assertIn("permissions:\n  contents: read", self.verify_job)
        self.assertNotIn("contents: write", self.verify_job)
        self.assertIn("permissions:\n      contents: write", self.release_job)
        self.assertEqual(self.workflow.count("contents: write"), 1)

    def test_pr_validation_uses_explicit_revisions_and_has_no_publish_flag(self):
        self.assertIn("github.event.pull_request.base.sha", self.verify_job)
        self.assertIn("github.event.pull_request.head.sha", self.verify_job)
        self.assertNotIn("--publish", self.verify_job)
        self.assertIn("fetch-depth: 0", self.verify_job)
        self.assertNotIn("pull_request_target", self.workflow)

    def test_ci_pins_actions_and_enforces_the_runtime_and_build_constraints(self):
        import re

        uses = re.findall(r"uses: (.+)", self.workflow)
        self.assertTrue(uses)
        for action in uses:
            self.assertRegex(action, r"@[0-9a-f]{40} # v[0-9]+\.[0-9]+\.[0-9]+$")
        self.assertNotRegex(self.workflow, r"uv run (?!\-\-locked)")
        self.assertIn("UV_BUILD_CONSTRAINT:", self.workflow)
        self.assertIn('python-version: "3.14"', self.workflow)
        self.assertIn("runs-on: macos-latest", self.workflow)

    def test_tagging_job_serializes_releases_and_fetches_all_tags(self) -> None:
        self.assertIn("concurrency:", self.release_job)
        self.assertIn("cancel-in-progress: false", self.release_job)
        self.assertIn("fetch-depth: 0", self.release_job)


if __name__ == "__main__":
    unittest.main()
