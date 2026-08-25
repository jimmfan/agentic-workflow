#!/usr/bin/env python3
"""Create and push one immutable release tag for a verified main commit."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
from typing import Iterable


VERSION_PATH = Path("skills/agent-workflow/VERSION")
SEMVER = re.compile(r"\d+\.\d+\.\d+")
FULL_SHA = re.compile(r"[0-9a-fA-F]{40}")
BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


class ReleaseError(RuntimeError):
    pass


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        errors="backslashreplace",
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ReleaseError(f"git {' '.join(args)} failed: {detail}")
    return result


def resolve_commit(revision: str, label: str) -> str:
    if FULL_SHA.fullmatch(revision) is None:
        raise ReleaseError(f"{label} must be a full 40-character commit SHA")
    resolved = git("rev-parse", "--verify", f"{revision}^{{commit}}").stdout.strip()
    if resolved != revision.lower():
        raise ReleaseError(f"{label} did not resolve to the expected commit")
    return resolved


def parse_version(value: str, label: str) -> tuple[int, int, int]:
    if SEMVER.fullmatch(value) is None:
        raise ReleaseError(f"{label} must use x.y.z; found {value!r}")
    major, minor, patch = value.split(".")
    return int(major), int(minor), int(patch)


def version_at(commit: str) -> str:
    return git("show", f"{commit}:{VERSION_PATH.as_posix()}").stdout.strip()


def version_changed(before: str, commit: str) -> bool:
    result = git(
        "diff",
        "--quiet",
        before,
        commit,
        "--",
        VERSION_PATH.as_posix(),
        check=False,
    )
    if result.returncode not in (0, 1):
        detail = result.stderr.strip() or result.stdout.strip()
        raise ReleaseError(f"could not compare VERSION across the push: {detail}")
    return result.returncode == 1


def semantic_tags() -> list[tuple[tuple[int, int, int], str]]:
    tags: list[tuple[tuple[int, int, int], str]] = []
    output = git("for-each-ref", "--format=%(refname:short)", "refs/tags").stdout
    for tag in output.splitlines():
        if tag.startswith("v") and SEMVER.fullmatch(tag[1:]):
            tags.append((parse_version(tag[1:], f"tag {tag}"), tag))
    return tags


def tag_exists(tag: str) -> bool:
    return git("show-ref", "--verify", "--quiet", f"refs/tags/{tag}", check=False).returncode == 0


def create_and_push_tag(tag: str, commit: str) -> None:
    git(
        "-c",
        f"user.name={BOT_NAME}",
        "-c",
        f"user.email={BOT_EMAIL}",
        "tag",
        "--annotate",
        "--message",
        f"Agent Workflow {tag}",
        tag,
        commit,
    )
    git("push", "origin", f"refs/tags/{tag}:refs/tags/{tag}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, help="push event's previous commit SHA")
    parser.add_argument("--commit", required=True, help="exact verified github.sha commit")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        before = resolve_commit(args.before, "--before")
        commit = resolve_commit(args.commit, "--commit")
        if not version_changed(before, commit):
            print("VERSION did not change in this push; no release tag requested.")
            return 0

        version_text = version_at(commit)
        requested = parse_version(version_text, "VERSION")
        tag = f"v{version_text}"

        if tag_exists(tag):
            raise ReleaseError(f"release tag {tag} already exists and will not be reused or moved")

        existing = semantic_tags()
        if existing:
            highest_version, highest_tag = max(existing)
            if requested <= highest_version:
                raise ReleaseError(
                    f"VERSION {version_text} must be greater than highest release tag {highest_tag}"
                )

        create_and_push_tag(tag, commit)
        print(f"Created annotated {tag} at verified commit {commit} and pushed only that tag.")
        return 0
    except ReleaseError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
