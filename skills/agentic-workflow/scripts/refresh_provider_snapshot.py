#!/usr/bin/env python3
"""Generate a reviewed provider snapshot outside the runtime install path."""

from __future__ import annotations

import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable

from provider_snapshot import SnapshotTreeError, tree_digest, validate_local_references


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DECLARATION = PACKAGE_ROOT / "payload" / "ai-workflow" / "providers.json"
MINIMUM_PYTHON = (3, 11)
GIT_OBJECT = re.compile(r"[0-9a-f]{40}")


class RefreshError(RuntimeError):
    pass


def run_gh(gh: str, arguments: list[str]) -> str:
    result = subprocess.run(
        [gh, *arguments],
        cwd=PACKAGE_ROOT,
        text=True,
        capture_output=True,
        errors="backslashreplace",
    )
    if result.returncode != 0:
        detail = " ".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
        raise RefreshError(f"gh {' '.join(arguments[:2])} failed: {detail}")
    return result.stdout


def api_json(gh: str, endpoint: str) -> dict[str, object]:
    try:
        value = json.loads(run_gh(gh, ["api", endpoint]))
    except json.JSONDecodeError as exc:
        raise RefreshError(f"GitHub API returned invalid JSON for {endpoint}") from exc
    if not isinstance(value, dict):
        raise RefreshError(f"GitHub API returned an unexpected value for {endpoint}")
    return value


def safe_path(value: object, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise RefreshError(f"invalid {label}: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise RefreshError(f"invalid {label}: {value!r}")
    return path


def load_declaration() -> tuple[str, str, str, str, str, list[tuple[str, str]]]:
    raw = json.loads(DECLARATION.read_text(encoding="utf-8"))
    provider = raw.get("provider") if isinstance(raw, dict) else None
    if not isinstance(provider, dict):
        raise RefreshError("provider declaration is incomplete")
    repository = provider.get("repository")
    version = provider.get("version")
    commit = provider.get("resolved_commit")
    tag_object = provider.get("tag_object")
    upstream_tree = provider.get("upstream_tree")
    skills_raw = provider.get("skills")
    if not isinstance(repository, str) or repository.count("/") != 1:
        raise RefreshError("provider repository must use owner/name form")
    if not isinstance(version, str) or not version:
        raise RefreshError("provider version must be a pinned tag")
    if not isinstance(commit, str) or GIT_OBJECT.fullmatch(commit) is None:
        raise RefreshError("provider resolved commit must be a full Git object ID")
    if not isinstance(tag_object, str) or GIT_OBJECT.fullmatch(tag_object) is None:
        raise RefreshError("provider tag object must be a full Git object ID")
    if not isinstance(upstream_tree, str) or GIT_OBJECT.fullmatch(upstream_tree) is None:
        raise RefreshError("provider upstream tree must be a full Git object ID")
    if not isinstance(skills_raw, list):
        raise RefreshError("provider skills must be an array")
    skills: list[tuple[str, str]] = []
    for item in skills_raw:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise RefreshError("provider skill entry is incomplete")
        path = safe_path(item.get("path"), f"path for {item['name']}")
        if path.name != item["name"]:
            raise RefreshError(f"provider skill path does not match its name: {item['name']}")
        skills.append((item["name"], path.as_posix()))
    return repository, version, commit, tag_object, upstream_tree, skills


def verify_tag(gh: str, repository: str, version: str, commit: str, tag_object: str) -> None:
    reference = api_json(gh, f"repos/{repository}/git/ref/tags/{version}")
    target = reference.get("object")
    if not isinstance(target, dict) or target.get("type") != "tag" or target.get("sha") != tag_object:
        raise RefreshError("upstream tag reference no longer matches the declared annotated tag object")
    tag = api_json(gh, f"repos/{repository}/git/tags/{tag_object}")
    tagged = tag.get("object")
    if not isinstance(tagged, dict) or tagged.get("type") != "commit" or tagged.get("sha") != commit:
        raise RefreshError("upstream tag object no longer resolves to the declared commit")


def generate(output: Path) -> None:
    if output == PACKAGE_ROOT or PACKAGE_ROOT in output.parents:
        raise RefreshError("output must be outside the Agentic Workflow package")
    if output.exists() or output.is_symlink():
        raise RefreshError(f"output must not already exist: {output}")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise RefreshError(f"output parent must be an existing safe directory: {output.parent}")
    gh = shutil.which("gh")
    if gh is None:
        raise RefreshError("GitHub CLI with `gh skill` is required for maintainer refresh")
    repository, version, commit, tag_object, upstream_tree, skills = load_declaration()
    verify_tag(gh, repository, version, commit, tag_object)
    commit_response = api_json(gh, f"repos/{repository}/git/commits/{commit}")
    commit_tree = commit_response.get("tree")
    if not isinstance(commit_tree, dict) or commit_tree.get("sha") != upstream_tree:
        raise RefreshError("upstream commit tree no longer matches the declaration")
    tree_response = api_json(gh, f"repos/{repository}/git/trees/{upstream_tree}?recursive=1")
    tree_entries = tree_response.get("tree")
    if not isinstance(tree_entries, list) or tree_response.get("truncated") is True:
        raise RefreshError("upstream recursive tree is missing or truncated")
    tree_shas = {
        item["path"]: item["sha"]
        for item in tree_entries
        if isinstance(item, dict)
        and item.get("type") == "tree"
        and isinstance(item.get("path"), str)
        and isinstance(item.get("sha"), str)
    }

    with tempfile.TemporaryDirectory(prefix="agentic-workflow-provider-refresh-", dir=output.parent) as temporary:
        generated = Path(temporary) / "snapshot"
        skills_root = generated / "skills"
        skills_root.mkdir(parents=True)
        for name, path in skills:
            run_gh(
                gh,
                ["skill", "install", repository, path, "--pin", version, "--dir", str(skills_root)],
            )
            installed = skills_root / name / "SKILL.md"
            if installed.is_symlink() or not installed.is_file():
                raise RefreshError(f"gh skill install omitted {name}")
            tree_sha = tree_shas.get(path)
            text = installed.read_text(encoding="utf-8")
            if not isinstance(tree_sha, str) or f"    github-tree-sha: {tree_sha}" not in text:
                raise RefreshError(f"installed {name} did not come from the declared commit")
            validate_local_references(skills_root / name)

        expected = {name for name, _path in skills}
        actual = {path.name for path in skills_root.iterdir()}
        if actual != expected:
            raise RefreshError("generated provider inventory differs from the declaration")

        license_response = api_json(gh, f"repos/{repository}/contents/LICENSE?ref={commit}")
        content = license_response.get("content")
        if not isinstance(content, str):
            raise RefreshError("upstream license response lacks content")
        try:
            license_bytes = base64.b64decode("".join(content.split()), validate=True)
        except ValueError as exc:
            raise RefreshError("upstream license response is not valid base64") from exc
        if b"MIT License" not in license_bytes:
            raise RefreshError("upstream license is no longer the reviewed MIT text")
        (generated / "LICENSE").write_bytes(license_bytes)

        digest = tree_digest(skills_root)
        generated.replace(output)

    print(f"Generated {output}")
    print(f"resolved_commit={commit}")
    print(f"snapshot_sha256={digest}")
    print(f"license_sha256={sha256(license_bytes).hexdigest()}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new directory to create for review")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    if sys.version_info < MINIMUM_PYTHON:
        print("ERROR: Agentic Workflow requires Python 3.11 or newer", file=sys.stderr)
        return 2
    try:
        args = build_parser().parse_args(argv)
        generate(args.output.resolve())
        return 0
    except (SnapshotTreeError, OSError, UnicodeError, json.JSONDecodeError, RefreshError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
