# ADR-0015: Adapt the effective Wayfinder instructions for local state

- Status: accepted
- Date: 2026-08-16
- Amends: ADR-0011, ADR-0013, and ADR-0014
- Amended by: ADR-0016

## Context

ADR-0011 made `.ai-workflow-state/wayfinder/<effort>/` the canonical local
Wayfinder representation with separate U#/D#/T# identities. ADR-0013 later
overlaid four provider metadata scalars so Agentic Workflow could select the
pinned Wayfinder skill implicitly. The provider method body remained unchanged.

That combination is not a coherent effective instruction set. When Codex
selects a skill it loads the complete `SKILL.md`, not only its activation
metadata. The pinned Wayfinder v1.2.3 body then says the tracker issue is
canonical, asks for tracker setup, uses `.scratch/` as its local fallback, and
treats each question as a decision ticket with issue assignment, comments,
closing, and tracker-native blocking. Those mechanics conflict with the local
storage contract and encourage an upstream decision question to be mistaken for
local executable T# work.

The compatible method is still valuable: destination orientation, a
low-resolution map, honest fog, incremental uncertainty resolution,
progressive loading, and a dependency-derived frontier. The adaptation must
preserve that method while making the configured local ontology operational.

Current Codex documentation also says same-named skills are not merged. A
separate wrapper therefore would not reliably adapt explicit `$wayfinder` use.

## Decision

Replace the metadata-only Wayfinder overlay declaration with one narrow
`wayfinder-local-state-v1` provider adapter. The adapter inserts a clearly
delimited authoritative local-mode section immediately before the unchanged
upstream method and applies the known activation metadata changes.

In local mode:

- `.ai-workflow-state/wayfinder/<effort>/` is the only canonical store;
- a sharp decision, investigation, research, prototype, grilling, or human
  clarification question is U#;
- resolving a U# creates or updates D# only for a durable project choice;
- upstream `task` or follow-on work becomes T# only when it is concretely
  executable and decomposition adds value;
- no U# -> D# -> T# sequence is mandatory;
- tracker setup, `.scratch/`, external issue mutation, labels, assignment,
  issue comments/closing, and tracker-native blocking do not apply;
- Wayfinder owns durable coordination while specialized capabilities may
  resolve or consume individual items; and
- Grilling and Domain Modeling run only when destination, human preference,
  terminology, or boundary ambiguity actually justifies them.

The declaration records the pinned upstream method-body SHA-256. Install and
update require that fingerprint plus the expected pinned source metadata and
activation values before changing anything. The exact adapted block is
idempotent. Unexpected body bytes, markers, source metadata, or activation
metadata fail closed before either provider file is written. Existing unrelated
files and metadata remain preserved. Status reports pending, ready, or
incompatible adaptation. Remove reports and preserves the provider directory.

## Consequences

Fresh Codex agents receive one operational model: Agentic Workflow owns routing
and local storage/re-entry, while upstream owns the method. Explicit and
automatic Wayfinder use now execute the same local ontology. A future provider
pin must deliberately review and update the body fingerprint and adapter
compatibility instead of applying an anchor optimistically.

The adapter is intentionally provider-specific. It is not a generic patch
framework, provider fork, ownership database, or upgrade engine. The upstream
body remains byte-for-byte intact after the inserted block, making future
comparison straightforward.

Provider directories remain independently owned and are never deleted or
rewritten on remove. If Agentic Workflow's local contract is absent, the
inserted section tells the skill to ignore local mode and follow the unchanged
upstream method.

## Alternatives considered

- Keep the metadata-only overlay: rejected because it changes selection while
  leaving contradictory operational instructions active.
- Rely only on root routing and the state contract: rejected because the loaded
  provider body remains the most specific workflow procedure.
- Add a separate local wrapper skill: rejected because explicit `$wayfinder`
  still targets the provider and same-named skills are not merged.
- Fork the complete Wayfinder skill: rejected because it duplicates the method
  and creates a larger drift surface than one reviewed local-mode block.
- Rewrite tracker paragraphs out of the provider body: rejected because it
  would obscure the upstream source and make provider upgrades harder to audit.
