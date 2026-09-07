#!/usr/bin/env python3
"""Validate a version change; optionally publish an immutable verified-main tag."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
from typing import Iterable


VERSION_PATH = Path("VERSION")
SEMVER = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
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
        raise ReleaseError(f"could not compare VERSION between base and head: {detail}")
    return result.returncode == 1


def semantic_tags() -> list[tuple[tuple[int, int, int], str]]:
    tags: list[tuple[tuple[int, int, int], str]] = []
    output = git("for-each-ref", "--format=%(refname:short)", "refs/tags").stdout
    for tag in output.splitlines():
        if tag.startswith("v") and SEMVER.fullmatch(tag[1:]):
            tags.append((parse_version(tag[1:], f"tag {tag}"), tag))
    return tags


def tag_exists(tag: str) -> bool:
    return (
        git(
            "show-ref", "--verify", "--quiet", f"refs/tags/{tag}", check=False
        ).returncode
        == 0
    )


def remote_tags() -> dict[str, str]:
    return {
        ref: sha
        for sha, ref in (
            line.split()
            for line in git("ls-remote", "--tags", "origin").stdout.splitlines()
        )
    }


def validate_release(before: str, commit: str) -> tuple[str | None, bool]:
    if not version_changed(before, commit):
        return None, False
    version_text = version_at(commit)
    requested = parse_version(version_text, "VERSION")
    previous = parse_version(version_at(before), "base VERSION")
    if requested <= previous:
        raise ReleaseError(f"VERSION {version_text} must be greater than base VERSION")
    tag = f"v{version_text}"
    ref = f"refs/tags/{tag}"
    remote = remote_tags()
    if tag_exists(tag):
        if (
            git("cat-file", "-t", ref).stdout.strip() != "tag"
            or git("rev-parse", f"{ref}^{{}}").stdout.strip() != commit
        ):
            raise ReleaseError(
                f"release tag {tag} already exists locally with conflicting type or commit"
            )
    if ref in remote:
        if remote.get(ref + "^{}") != commit:
            raise ReleaseError(
                f"release tag {tag} already exists remotely with conflicting type or commit"
            )
        return tag, True
    existing = semantic_tags()
    for remote_ref in remote:
        name = remote_ref.removeprefix("refs/tags/")
        if name.startswith("v") and SEMVER.fullmatch(name[1:]):
            existing.append((parse_version(name[1:], name), name))
    existing = [(version, name) for version, name in existing if name != tag]
    if existing and requested <= max(existing)[0]:
        raise ReleaseError(
            f"VERSION {version_text} must be greater than highest release tag {max(existing)[1]}"
        )
    return tag, False


def create_and_push_tag(tag: str, commit: str) -> None:
    if not tag_exists(tag):
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
    # A local tag left by a failed push is pending publication, never success by itself.
    git("push", "origin", f"refs/tags/{tag}:refs/tags/{tag}")
    if remote_tags().get(f"refs/tags/{tag}^{{}}") != commit:
        raise ReleaseError(f"remote publication of {tag} could not be verified")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base", required=True, help="explicit PR base or push previous commit SHA"
    )
    parser.add_argument(
        "--head",
        required=True,
        help="explicit PR head or exact verified main commit SHA",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="publish after validation (verified main workflow only)",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        before = resolve_commit(args.base, "--base")
        commit = resolve_commit(args.head, "--head")
        tag, published = validate_release(before, commit)
        if tag is None:
            print("VERSION did not change; no release tag requested.")
        elif published:
            print(
                f"Annotated {tag} is already published at {commit}; no changes needed."
            )
        elif not args.publish:
            print(
                f"Validated {tag} for {commit}; publication is pending; no refs written."
            )
        else:
            # Publication runs the same validation afresh, regardless of an earlier PR result.
            create_and_push_tag(tag, commit)
            print(
                f"Created annotated {tag} at verified commit {commit} and verified remote publication."
            )
        return 0
    except ReleaseError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
