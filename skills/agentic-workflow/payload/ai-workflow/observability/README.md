# Optional workflow observability

This optional analyzer answers a narrow question: which instrumented skills and
model/tool resources were actually observed across exported agent runs? It
normalizes existing OpenTelemetry data into deterministic metadata-only text or
JSON. Success is a report containing provenance, observed skill sequences,
model calls, requested and response models, token breakdowns, duration, tool
calls, and errors without prompt, response, repository, or workspace values.

Nothing here participates in routing. Installation does not enable telemetry,
change an editor setting, start a process, create a database, inspect source
files, or write analytics data into the project. `analyze.py` reads the files
you explicitly name and writes only to standard output. It requires Python
3.11 or newer and uses no third-party Python packages.

## Supported inputs and trust levels

The analyzer accepts:

- standard OTLP trace JSON as one object or JSON Lines, the preferred stable
  interchange boundary;
- the current VS Code/Copilot append-only file-exporter JSON Lines shape,
  labeled `preview-raw` because the monitoring feature and serialized SDK
  object shape are Preview;
- one manually exported Agent Debug session, labeled `debug-converted` because
  that export can use synthetic parentage and omit token detail.

Current stable VS Code 1.133.x is the primary known-good baseline. The analyzer
does not gate on a VS Code version: it detects token, skill-attribution, and
model-metadata capabilities in each input. Missing optional attributes produce
partial metrics and an explicit capability/warning entry rather than failing
the analysis. It does not carry substantial compatibility machinery for older
VS Code telemetry formats.

It intentionally does not read the live Copilot SQLite databases, OTLP
protobuf, or arbitrary editor logs. The native span database schema is not a
documented compatibility boundary, and Agent Debug or Chat Debug logs can
contain full prompts and tool payloads.

Analysis is an offline linear pass. It loads one source document at a time and
retains normalized spans across all named inputs, so peak memory grows with the
largest raw input plus the total span count. Use a closed bounded snapshot for
local analysis; use an existing collector/backend for large or continuous
telemetry.

The implementation is cross-platform by design and hermetic fixtures cover
UTF-8 with a BOM, Windows CRLF and Windows-style paths, Unix LF, Linux paths,
and macOS paths. It has been live-tested only on Apple Silicon macOS, not on a
Windows or Linux host. It uses no shell utility or VS Code installation path.

Skill use is reported only when telemetry contains the current VS Code
`github.copilot.tool.parameters.skill_name` attribute or the current Copilot
CLI `github.copilot.skill.invoked` event. `(no skill event observed)` is not a
claim that the route was direct; an exporter or host might not supply skill
telemetry.

## Analyze an existing export

This read-only step converts the chosen export to a report. On macOS or Linux,
run it in the **host Terminal from the installed project root**, unless the
project and export exist only inside a Dev Container; in that case use the
**VS Code terminal inside that Dev Container**. It makes no persistent change:

```bash
python3 ai-workflow/observability/analyze.py /absolute/path/to/copilot-otel.jsonl
```

On native Windows, run the equivalent read-only command in **PowerShell from
the installed project root**:

```powershell
py -3 ai-workflow/observability/analyze.py "C:\absolute\path\to\copilot-otel.jsonl"
```

Success exits 0 and starts with `Agentic Workflow observability report`. An
unsupported or malformed export exits 2 and names the input number without
printing its path. If a live JSONL file ends with a partially written record,
the analyzer ignores only that last record and emits a warning; copying or
closing the export first produces a reproducible snapshot.

Use deterministic JSON for scripts. The following command is also read-only
and writes JSON to the terminal:

```bash
python3 ai-workflow/observability/analyze.py --format json /absolute/path/to/copilot-otel.jsonl
```

The output contains pseudonymous identifiers derived from normalized span
metadata rather than input paths, content, or raw trace IDs. It has no
generation timestamp, so identical inputs and tags produce identical bytes.
Redirecting standard output to a file is an explicit user-owned storage choice;
keep that report outside the consuming repository if it should remain local
analytics data.

## Opt in to the VS Code file exporter

Only enable capture when the native Agent Debug summary is insufficient and a
cross-run comparison is worth the Preview compatibility and disk-growth cost.
The file exporter is append-only and has no rotation. Choose a path outside all
source repositories, do not point multiple VS Code processes at the same file,
and keep content capture disabled.

In the **VS Code window that runs Copilot**, open the Command Palette and run
`Preferences: Open User Settings (UI)`. Search for each full setting ID and set
these persistent user-profile values:

1. Enable `github.copilot.chat.otel.enabled`.
2. Set `github.copilot.chat.otel.exporterType` to `file`.
3. Set `github.copilot.chat.otel.outfile` to an absolute path outside every
   repository, such as a file in a private temporary analytics directory.
4. Confirm `github.copilot.chat.otel.captureContent` is disabled.
5. Confirm `github.copilot.chat.otel.dbSpanExporter.enabled` is disabled; the
   analyzer does not need it.

Run `Developer: Reload Window` from the Command Palette so the exporter starts
with the reviewed settings. Reloading is temporary editor interruption; the
settings remain persistent until reversed. In a Dev Container, these settings
and the absolute output path belong to the remote VS Code extension environment
if the Settings UI marks them as Remote. The analyzer must then run in that same
container or read a copied snapshot from the host.

The first agent request made after opt-in should append newline-delimited JSON
to the selected path. That request can consume normal Copilot credits; do not
manufacture work merely to test telemetry. After naturally completing a run,
invoke the analyzer. A report with at least one run verifies the complete path.
If no file or spans appear, first inspect `GitHub Copilot Chat` in the VS Code
Output panel and recheck the five setting values before changing extensions or
credentials.

To reverse capture, use `Preferences: Open User Settings (UI)` in that same VS
Code environment, disable `github.copilot.chat.otel.enabled`, and run
`Developer: Reload Window`. This stops future telemetry but leaves the selected
export file untouched. After retaining any needed report, remove that exact
file with the host or container file manager to reclaim its space. Do not
delete Copilot authentication, Keychain entries, `CODEX_HOME`, `session-store.db`,
or editor WebStorage as part of this observability lifecycle.

## Manual Agent Debug export

For an occasional single-session diagnosis, prefer the native Agent Debug
panel described in the [VS Code Agent Debug Logs documentation](https://code.visualstudio.com/docs/agents/agent-troubleshooting/chat-debug-view).
Use its Export action to save one session outside the repository, then pass the
JSON file to `analyze.py`. The export may contain prompt, response, and tool
content even when OTel content capture is off. The analyzer discards known
content-bearing fields and never echoes their values, but the source export
itself remains sensitive and should be deleted through the file manager when no
longer needed.

## Token accounting

The report sums unique `chat` spans, never their aggregate `invoke_agent`
parent, so nested agents and repeated snapshots are not double-counted.
Cache-read and cache-creation tokens are reported as input-token subsets;
reasoning tokens are reported as an output-token subset. They are not added to
input or output totals. When tokenized chat spans are absent, an outermost
`invoke_agent` total is used only as the visibly labeled
`outer-invoke-fallback`. Missing token attributes produce a partial-coverage
warning rather than an invented zero-cost conclusion.

## Controlled comparisons

Decide the task fixture, variants, acceptance check, model, repository revision,
and stopping rule before collecting data. Restore the same revision and initial
state for each run, use a new agent session, keep content capture off, and save
one export snapshot per variant. Repeat runs because model behavior is noisy.

Tags are user assertions for experiment provenance; the analyzer does not
verify them. Use only non-sensitive values. This read-only macOS/Linux command
labels one report:

```bash
python3 ai-workflow/observability/analyze.py --format json \
  --tag experiment=route-contract-v1 \
  --tag variant=skill-telemetry \
  --tag framework=0.7.1 \
  --tag verification=pass \
  /absolute/path/to/closed-variant-export.jsonl
```

On native Windows PowerShell, place the same options on one line after
`py -3 ai-workflow/observability/analyze.py`. Compare the raw group medians and
review the actual verification evidence; do not collapse tokens, correctness,
and duration into an unvalidated “efficiency score.” A tagged
`verification=pass` is only trustworthy when it refers to a separately reviewed
acceptance result.

## Privacy and failure boundaries

The normalizer whitelists operation, model, token, skill, timing, service
version, and error-status metadata. It counts and discards known content and
repository/workspace fields, sanitizes skill identifiers, pseudonymizes run and
input identities, and never emits raw trace, conversation, request, repository,
or path identifiers. Tags are the only user-provided strings copied to output.

Because VS Code monitoring, Agent Debug export, Copilot-specific attributes,
and GenAI semantic conventions can change, `unknown non-span shape` is a
compatibility warning and `contains no supported spans` is a hard failure. Do
not interpret a zero or missing field as improved performance. Preserve a
content-free fixture from each validated exporter version when updating the
adapter, update its tests and provenance rules, and prefer standard OTLP over a
new private-storage parser.

The current feature evidence and the BUILD SMALLER decision are recorded in the
source package's maintainer observability decision document; that document is
not installed into consuming repositories.
