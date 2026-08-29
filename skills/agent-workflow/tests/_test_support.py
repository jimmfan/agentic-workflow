from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CLI = PACKAGE_ROOT / "cli.py"
ADOPT = PACKAGE_ROOT / "scripts" / "adopt.py"
BOOTSTRAP = PACKAGE_ROOT / "scripts" / "bootstrap.py"
LIFECYCLE = PACKAGE_ROOT / "scripts" / "lifecycle.py"
PROVIDERS = PACKAGE_ROOT / "scripts" / "providers.py"
REFRESH_PROVIDERS = PACKAGE_ROOT / "scripts" / "refresh_provider_snapshot.py"
MANAGED_BEGIN = b"<!-- agent-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- agent-workflow:managed-end -->\n"
IMPLICIT_INVOCATION_SKILLS = ("to-spec", "to-tickets", "implement")
USER_ONLY_SKILLS = ("setup-matt-pocock-skills", "teach", "triage")


def run_script(
    script: Path,
    *arguments: object,
    env: dict[str, str] | None = None,
    encoding: str = "utf-8",
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(str(item) for item in arguments)],
        text=True,
        capture_output=True,
        encoding=encoding,
        errors="strict",
        env=env,
        cwd=cwd,
    )


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def tree_snapshot(root: Path) -> dict[str, tuple[str, bytes | str]]:
    result: dict[str, tuple[str, bytes | str]] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory", b"")
        else:
            result[relative] = ("file", path.read_bytes())
    return result


class ProjectTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def adopt(self, command: str, *extra: object) -> subprocess.CompletedProcess[str]:
        return run_script(ADOPT, command, self.project, *extra)

    def assert_ok(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def copy_package(self, name: str) -> Path:
        package_copy = Path(self.temporary.name) / name / "agent-workflow"
        shutil.copytree(PACKAGE_ROOT, package_copy)
        return package_copy

    def declared_provider_names(self, package_root: Path = PACKAGE_ROOT) -> set[str]:
        declaration = package_root / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        return {item["name"] for item in raw["provider"]["skills"]}

    def run_fake_provider_refresh(
        self,
        name: str,
        *,
        mutation: str | None = None,
    ) -> tuple[object, Path]:
        package_copy = self.copy_package(name)
        declaration = package_copy / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        provider = raw["provider"]
        skill_name = "demo"
        skill_path = "skills/engineering/demo"
        skill_tree = "1" * 40
        provider["skills"] = [{"name": skill_name, "path": skill_path}]
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        upstream_skill = b"---\ndescription: Demo skill.\nname: demo\n---\n\nDemo body.\n"
        upstream_openai = b'interface:\n  display_name: "Demo"\n'
        metadata = (
            "metadata:\n"
            f"    github-path: {skill_path}\n"
            f"    github-pinned: {provider['version']}\n"
            f"    github-ref: refs/tags/{provider['version']}\n"
            f"    github-repo: https://github.com/{provider['repository']}\n"
            f"    github-tree-sha: {skill_tree}\n"
        ).encode("utf-8")
        installed_skill = upstream_skill.replace(
            b"name: demo\n", metadata + b"name: demo\n"
        )

        def git_blob_sha(content: bytes) -> str:
            header = f"blob {len(content)}\0".encode("ascii")
            return hashlib.sha1(header + content).hexdigest()

        tree_entries = [
            {"path": skill_path, "mode": "040000", "type": "tree", "sha": skill_tree},
            {
                "path": f"{skill_path}/SKILL.md",
                "mode": "100644",
                "type": "blob",
                "sha": git_blob_sha(upstream_skill),
            },
            {
                "path": f"{skill_path}/agents",
                "mode": "040000",
                "type": "tree",
                "sha": "2" * 40,
            },
            {
                "path": f"{skill_path}/agents/openai.yaml",
                "mode": "100644",
                "type": "blob",
                "sha": git_blob_sha(upstream_openai),
            },
        ]

        scripts = package_copy / "scripts"
        sys.path.insert(0, str(scripts))
        try:
            refresh = load_module(
                f"agent_workflow_refresh_{name}",
                scripts / "refresh_provider_snapshot.py",
            )
        finally:
            sys.path.pop(0)
        refresh.shutil.which = lambda _command: "/fake/gh"

        def fake_run_gh(_gh: str, arguments: list[str]) -> str:
            if arguments[0] == "api":
                endpoint = arguments[1]
                responses = {
                    f"repos/{provider['repository']}/git/ref/tags/{provider['version']}": {
                        "object": {"type": "tag", "sha": provider["tag_object"]}
                    },
                    f"repos/{provider['repository']}/git/tags/{provider['tag_object']}": {
                        "object": {"type": "commit", "sha": provider["resolved_commit"]}
                    },
                    f"repos/{provider['repository']}/git/commits/{provider['resolved_commit']}": {
                        "tree": {"sha": provider["upstream_tree"]}
                    },
                    f"repos/{provider['repository']}/git/trees/{provider['upstream_tree']}?recursive=1": {
                        "tree": tree_entries,
                        "truncated": False,
                    },
                    f"repos/{provider['repository']}/contents/LICENSE?ref={provider['resolved_commit']}": {
                        "content": base64.b64encode(b"MIT License\n").decode("ascii")
                    },
                }
                return json.dumps(responses[endpoint])
            self.assertEqual(arguments[:2], ["skill", "install"])
            target = Path(arguments[arguments.index("--dir") + 1]) / skill_name
            (target / "agents").mkdir(parents=True)
            (target / "SKILL.md").write_bytes(installed_skill)
            installed_openai = upstream_openai
            if mutation == "modified":
                installed_openai += b"changed: true\n"
            (target / "agents/openai.yaml").write_bytes(installed_openai)
            if mutation == "extra":
                (target / "extra.md").write_text("unexpected\n", encoding="utf-8")
            if mutation == "extra-directory":
                (target / "empty").mkdir()
            return ""

        refresh.run_gh = fake_run_gh
        output = Path(self.temporary.name) / f"{name}-candidate"
        return refresh, output
