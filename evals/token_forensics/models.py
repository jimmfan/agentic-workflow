"""Small normalized trace model shared by parsers and analyses."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


UsageSemantics = Literal["per_turn", "cumulative_snapshot"]


@dataclass(frozen=True)
class UsageObservation:
    sequence: int
    line_number: int
    semantics: UsageSemantics
    input_tokens: int | None = None
    cached_input_tokens: int | None = None
    cache_write_input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_output_tokens: int | None = None
    model_context_window: int | None = None


@dataclass(frozen=True)
class ToolInvocation:
    invocation_id: str
    sequence: int
    tool_type: str
    name: str
    command: str | None
    status: str | None
    exit_code: int | None
    stdout_bytes: int | None = None
    stderr_bytes: int | None = None
    combined_output_bytes: int | None = None
    duration_ms: float | None = None
    changed_paths: tuple[tuple[str, str], ...] = ()

    @property
    def output_bytes(self) -> int:
        if self.stdout_bytes is not None or self.stderr_bytes is not None:
            return (self.stdout_bytes or 0) + (self.stderr_bytes or 0)
        return self.combined_output_bytes or 0


@dataclass(frozen=True)
class CompactionEvent:
    sequence: int
    line_number: int
    event_type: str


@dataclass
class NormalizedTrace:
    source_path: Path
    source_format: str
    source_bytes: int
    thread_id: str | None = None
    event_type_counts: dict[str, int] = field(default_factory=dict)
    codex_turns_started: int = 0
    codex_turns_completed: int = 0
    usage_observations: list[UsageObservation] = field(default_factory=list)
    tool_invocations: list[ToolInvocation] = field(default_factory=list)
    compactions: list[CompactionEvent] = field(default_factory=list)
    agent_messages: list[str] = field(default_factory=list)
    parse_warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Thresholds:
    """Simple warning thresholds; callers may replace values in tests or local use."""

    large_tool_output_bytes: int = 512 * 1024
    large_total_tool_output_bytes: int = 5 * 1024 * 1024
    repeated_command_count: int = 3
    repeated_failed_command_count: int = 2
    repeated_resource_count: int = 3
    high_tool_call_count: int = 50
    long_codex_turn_count: int = 25
    large_framework_output_bytes: int = 256 * 1024


JsonObject = dict[str, Any]
