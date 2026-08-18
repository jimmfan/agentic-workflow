# ADR-0020: Own the declared provider projection

- Status: accepted
- Date: 2026-08-17
- Last amended: 2026-08-17
- Supersedes: ADR-0014, ADR-0015, ADR-0017, and ADR-0018
- Amends: ADR-0007, ADR-0010, ADR-0011, and ADR-0013
- Related: ADR-0021

## Context

Agentic Workflow routes to a reviewed set of 14 Matt Pocock skills shared by
Codex and GitHub Copilot through `.agents/skills/`. The raw upstream snapshot is
pinned and valuable, but several effective host contracts differ intentionally:
Wayfinder uses project-local state, and routed Wayfinder, To Spec, To Tickets,
and Implement must be available for model invocation. In particular, raw
Wayfinder carries `disable-model-invocation: true`, which can hide it from a
Claude model running inside the GitHub Copilot VS Code host even though that
host otherwise supports the shared skill directory.

Earlier decisions treated any existing same-named directory as independently
owned. A raw upstream directory, an older adapted directory, or a local change
therefore became a conflict requiring manual reconciliation. That behavior
optimized for hypothetical independent owners at the expense of the sole
supported use: the declaration describes one framework-produced, reconstructable
provider projection. It also allowed the router to select a provider whose
effective metadata the lifecycle refused to repair.

## Decision

The declared provider directories are framework-owned, replaceable build output.
The pinned unmodified snapshot and MIT notice remain release inputs; Agentic
Workflow creates the effective projection by applying its reviewed Wayfinder
local-mode and implicit-invocation adapters in staging.

The maintainer and CI release gate validates the bundled checksum, provenance,
and MIT license against the reviewed release identity. These release bookkeeping
checks do not run again in an end-user lifecycle operation.

Install and update:

1. validate the exact inventory, safe regular-file shape, local references, and
   adapter preconditions needed to build a usable projection;
2. stage and validate the complete effective 14-skill projection on the target
   filesystem;
3. classify each declared destination as `ready`, `repairable` (missing or
   different), or `blocked` (an unsafe path such as a symlink or non-directory);
4. if any destination is blocked, change none of the declared set; otherwise
   replace every repairable directory as one transaction and restore the prior
   projection if a move fails; and
5. leave exact ready directories untouched and preserve every unrelated
   `.agents/skills/` directory.

Remove deletes exactly the declared provider directories as one reversible
filesystem operation and preserves unrelated skills. There is no ownership
database, adoption flow, legacy migration, runtime network acquisition, or
manual reconciliation path. Changes inside a declared directory are overwritten
on install or update because that directory is reconstructable framework output,
not a user-owned customization boundary.

The transaction commits when the target projection has been replaced or
removed. Failure before that point restores prior paths where possible. Failure
to delete the now-obsolete recovery directory after commit reports a warning
and the exact retained path, but does not falsely report that the committed
target mutation failed.

The Wayfinder adapter keeps the upstream planning method while making the local
contract authoritative. Upstream decision and investigation tickets map to U#;
T# is reserved for concrete executable work, and existing IDs are never
renumbered to change classification. The map stays the self-contained
coordination/re-entry point and links to canonical specifications, research,
ADRs, code, tests, and evidence rather than copying or outsourcing its state.

The invocation adapters make Wayfinder, To Spec, To Tickets, and Implement
model-invocable on Codex and GitHub Copilot. Setup, Teach, and Triage remain
user-only. Claude Code remains declared unavailable; this decision concerns a
Claude model hosted by GitHub Copilot, not native Claude Code. Selection,
invocation capability, authorization, and execution remain distinct, and an
unavailable provider must never be reported as executed.

Implement and Code Review have no hard issue-tracker prerequisite: each can
consume a supplied or repository-local specification, and review can report a
missing specification explicitly. To Spec and To Tickets retain tracker
configuration because they publish tracker-native artifacts.

Provider setup remains best-effort relative to the core router. A provider
failure is reported truthfully but does not roll back a successful core update.

## Consequences

Fresh, partial, raw-upstream, modified, and older adapted installations converge
on the same tested effective projection without user cleanup. The specific
GitHub Copilot/Claude failure caused by raw Wayfinder's disabled invocation
metadata is repairable by normal update. Runtime remains offline and does not
fork upstream methodology: the bundle preserves pinned upstream bytes, while
small fingerprinted adapters define the intentional integration differences.

Users must put custom skills in differently named directories; edits inside the
14 declared names are disposable. Unsafe filesystem objects fail closed.
Runtime does not block provider setup on duplicated release checksums; a bad
checked-in snapshot fails the maintainer gate before release. A live GitHub
Copilot/Claude run is still required before claiming that editor and model
combination has been validated end to end.

## Alternatives considered

- Preserve differing declared directories and require manual reconciliation:
  rejected because it prevents normal update from repairing the exact host
  compatibility failures the framework owns.
- Add an ownership database or adoption workflow: rejected because the complete
  declared set is already the ownership boundary and no current user needs
  package-manager-grade coexistence.
- Fork the upstream repository: rejected because a pinned snapshot plus narrow,
  reviewed adapters has a much smaller maintenance and drift surface.
- Project a second copy under `.claude/skills/`: rejected because GitHub Copilot
  uses the shared `.agents/skills/` surface; model choice inside that host does
  not make native Claude Code's discovery layout relevant.
