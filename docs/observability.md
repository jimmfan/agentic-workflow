# Optional observability

## Decision and boundary

**BUILD SMALLER.** Agentic Workflow ships one inert, read-only analyzer for
existing VS Code, Copilot, and OTLP telemetry. Native Agent Debug remains the
single-session diagnostic UI, and an existing OTLP backend remains the
production storage/dashboard path. The framework adds only workflow-aware,
privacy-reduced normalization across exported runs.

The resulting architecture is:

```text
VS Code / Copilot / OTel
        ↓ existing telemetry generation
Agentic Workflow metadata analyzer
        ↓
workflow-aware normalized metrics
```

There is no telemetry generation, collector, database, dashboard, hook,
extension, watcher, daemon, or background process. The router and workflow
skills neither import nor invoke the analyzer.

## Compatibility baseline and validation status

Current stable **VS Code 1.133.x is the primary known-good baseline**. The
adapter recognizes capabilities and field shapes rather than checking an exact
VS Code version. Older or future exports can still produce partial results when
their span envelope is supported and optional attributes are absent.

The distinction between validation levels is deliberate:

- **Live-tested on this operating system:** package execution with Python
  3.12.13 (the package minimum is 3.11), parsing, reports, privacy behavior,
  installation lifecycle, and the full hermetic suite were run on Apple
  Silicon macOS. The installed VS Code 1.133.x and bundled Copilot
  source/configuration were inspected locally.
- **Cross-platform by design/test fixtures:** the analyzer uses only Python
  standard-library JSON, `pathlib`, and in-memory normalization. Hermetic tests
  cover UTF-8 with and without a BOM, Windows CRLF and Windows-style paths, Unix
  LF, Linux paths, and macOS paths. It uses no shell utility, OS-specific path,
  VS Code installation layout, filesystem lock behavior, or Unix-only API.
- Windows and Linux were **not live-tested**. Fixture coverage is not presented
  as host validation.
- No authenticated telemetry run was manufactured. Local OTel was disabled and
  no standalone Copilot CLI or existing export was available. Current skill
  fields are documentation/source validated plus fixture tested, not claimed as
  a live emission result.

## Supported inputs

The intentionally narrow input contract is:

1. Standard OTLP trace JSON or JSON Lines using `resourceSpans`, `scopeSpans`,
   and spans.
2. The current VS Code/Copilot 1.133.x raw append-only JSON Lines span shape,
   labeled `preview-raw` because monitoring and SDK serialization are Preview.
3. A manually exported Agent Debug session, labeled `debug-converted` because
   parentage and token detail can be lossy.

The analyzer ignores recognized metric/log records and summarizes spans. It
does not parse OTLP protobuf, the live/internal Copilot SQLite databases,
arbitrary debug logs, historical VS Code telemetry variants, or AHP-specific
messages. It is a small adapter, not a generic OpenTelemetry ingestion
framework.

An entirely unknown source with no supported spans fails visibly. Missing
optional telemetry does not fail the run.

## Capability-based degradation

Every report declares observed input capabilities:

- `token_usage`: `available`, `partial`, or `unavailable`;
- `skill_attribution`: `available` or `unavailable`;
- `model_metadata`: `available` or `unavailable`.

For example, supported chat spans with token usage and tool calls but no current
skill field still produce token, tool, duration, and error metrics. The report
warns that skill attribution is unavailable and uses `none-observed`; it never
mislabels absence as a direct route. Missing model attributes similarly leave
model fields unknown without discarding other metrics.

Current recognized skill signals are the VS Code
`github.copilot.tool.parameters.skill_name` span attribute and Copilot CLI
`github.copilot.skill.invoked` event with `github.copilot.skill.name`. No
compatibility logic depends on a VS Code version number.

## Accounting contract

The analyzer builds runs from outer `invoke_agent` spans and descendants,
deduplicates `(trace_id, span_id)` across overlapping snapshots, and sums unique
tokenized `chat` spans. It never adds parent `invoke_agent` aggregates to child
usage. Nested-agent chats therefore count once.

When tokenized chat spans are absent, an outer invocation total is used only as
the labeled `outer-invoke-fallback`. Cache-read and cache-creation tokens remain
input subsets; reasoning tokens remain an output subset. Missing data is `null`,
not an invented zero. Reports also retain requested and response model IDs,
tool calls, subagent calls, duration, error spans, observed skill sequence,
service/version metadata, and experiment tags.

Automated verification success, edit survival, follow-up/correction count, and
no-revert outcomes remain out of scope because current sources do not provide a
stable per-run correlation contract. A user-supplied experiment tag is an
assertion, not independently verified telemetry.

## Privacy, storage, and performance

Content capture stays off. The normalizer whitelists operation, model, token,
timing, skill, service/version, and error-status metadata. It discards known
prompt, response, tool-content, repository, workspace, working-directory, and
skill-path fields; sanitizes skill names; and emits pseudonymous input/run IDs
instead of raw paths, trace IDs, request IDs, or conversation IDs.

The analyzer reads only paths explicitly supplied on its command line and
writes only standard output. It creates no report, cache, database, or project
state. Input files and redirected output remain user-owned and should live
outside consuming repositories. Identical inputs and tags produce deterministic
JSON because no generation timestamp is added.

Analysis is an offline linear pass. It loads one source document at a time and
retains normalized spans for the named inputs. The local file exporter itself
is append-only and unrotated; use bounded closed snapshots locally and an
existing collector/backend for large or continuous telemetry.

## Maintenance and reversal

Exporter compatibility is isolated in `.ai-workflow/observability/analyze.py`.
Preserve content-free fixtures for the 1.133.x raw shape and standard OTLP
boundary. Add a new mapping only for a demonstrated current need; do not grow a
historical format library. Unknown structural drift should remain visible,
while missing optional capabilities should degrade as described above.

The installed guide contains complete capture, analysis, verification,
experiment, disable, and cleanup procedures. Removing the two framework-owned
observability files in a normal future release requires no data migration and
does not change routing behavior.

## Primary references

- [VS Code 1.133 release](https://code.visualstudio.com/updates/v1_133)
- [Agent Debug Logs](https://code.visualstudio.com/docs/agents/agent-troubleshooting/chat-debug-view)
- [Monitor agents with OpenTelemetry](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)
- [GitHub Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/README.md)
