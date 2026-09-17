"""Observe native rollout failures for bounded evaluations, without grading behavior."""

from __future__ import annotations

import json
from pathlib import Path

from evals.persistence import snapshot


class NativeExecutionMonitor:
    """Inspect new parent/child tool results; returning a status stops the runner."""

    def __init__(
        self, home: Path, project: Path, *, read_only=False, canaries=(), events=None
    ):
        self.home = home
        self.project = project
        self.canaries = tuple(canaries)
        self.before = snapshot(project) if read_only else None
        self.before_git = snapshot(project / ".git") if read_only else None
        self.offsets = {}
        self.failure = None
        self.events = events

    def __call__(self):
        if self.failure:
            return self.failure["status"]
        if self.before is not None and (
            snapshot(self.project) != self.before
            or snapshot(self.project / ".git") != self.before_git
        ):
            self.failure = {
                "status": "isolation-failure",
                "reason": "The read-only project changed during execution.",
            }
            return self.failure["status"]
        paths = sorted((self.home / "sessions").rglob("*.jsonl"))
        if self.events is not None and self.events.exists():
            paths.append(self.events)
        for path in paths:
            with path.open("rb") as stream:
                stream.seek(self.offsets.get(path, 0))
                while line := stream.readline():
                    if not line.endswith(b"\n"):
                        break
                    self.offsets[path] = stream.tell()
                    event = json.loads(line)
                    payload = event.get("payload", {})
                    kind = payload.get("type")
                    if kind in ("function_call_output", "custom_tool_call_output"):
                        observed = json.dumps(payload.get("output", ""))
                        if any(canary in observed for canary in self.canaries):
                            reason, status = (
                                "A denied canary was disclosed by a tool.",
                                "isolation-failure",
                            )
                        elif any(
                            failure in observed.lower()
                            for failure in (
                                "sandbox_apply:",
                                "invalid active developer path",
                                "errno::eperm",
                                "library not loaded:",
                                "(blocked by sandbox)",
                                "fatal: unable to access",
                                "you've hit your usage limit",
                                "insufficient_quota",
                                "failed to spawn agent",
                            )
                        ):
                            reason, status = observed[:1000], "infrastructure-blocked"
                        else:
                            continue
                    elif event.get("type") in ("error", "turn.failed"):
                        reason, status = (
                            json.dumps(event)[:1000],
                            "infrastructure-blocked",
                        )
                    elif event.get("type") == "event_msg" and kind in (
                        "error",
                        "turn_aborted",
                    ):
                        reason, status = (
                            json.dumps(payload)[:1000],
                            "infrastructure-blocked",
                        )
                    else:
                        continue
                    self.failure = {
                        "status": status,
                        "reason": reason,
                        "trace": path.relative_to(self.home).as_posix()
                        if path.is_relative_to(self.home)
                        else path.name,
                        "offset": self.offsets[path],
                    }
                    return status
        return None
