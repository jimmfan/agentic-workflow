# ADR-0028: Use Wayfinder as the sole durable coordinator

- Status: accepted
- Date: 2026-08-20
- Consolidated: 2026-08-22

## Context

Agent Workflow previously maintained separate DEC, DBG, and IMP continuity
systems alongside Wayfinder. Those systems created competing resume identities,
statuses, archive rules, and lifecycle behavior. Specialists already own better
methods and native artifacts than a coordinator could reproduce, so copying
their procedures into Wayfinder would increase context and create drift.

The project needs one small coordination owner, not mandatory durable state for
every method that might help during an effort.

## Decision

Wayfinder is the sole framework-owned durable coordination model. It persists
only consequential cross-session coordination: destination and scope, semantic
territory, current blockers and dependencies, useful frontier and next work,
optional current knowledge, and readable pointers to canonical artifacts.

Discovery, Debugging, Research, Prototype, Domain Modeling, Implementation,
Verification, and other specialists own their methods and native outputs. They
remain stateless from the framework's perspective and do not create competing
continuity notebooks merely because they run. Direct reasoning remains valid;
load only a specialist whose method materially helps the current frontier.

Native artifacts retain their own durable ownership. In particular,
`to-tickets` owns executable decomposition and its frontier; Wayfinder may link
that output but never mirrors T# work as a second ticket/status surface.
Specifications, research, reviews, learning workspaces, and optional accepted
IDP opportunity records are likewise canonical outputs rather than competing
framework coordination models.

When interrupted work lacks a sufficient canonical artifact, Wayfinder records
only the consequential return frontier and pointers. Existing DEC, DBG, IMP,
active-index, record, and archive files remain opaque project-owned historical
data. Current workflows neither resume nor migrate them, and no compatibility
parser or replacement specialist record is added.

## Consequences

Fresh sessions have one framework re-entry model. Standalone specialist work is
ephemeral unless it crosses the Wayfinder threshold, while specialist
methodology stays in the skill that owns it.

This decision does not require Wayfinder's current Markdown representation.
Representation and re-entry are governed separately by ADR-0011, so either
choice may change without silently changing the other.

Exact specialist lists, legacy record mechanics, implementation handoffs,
context budgets, and evaluation outcomes belong in runtime instructions,
contracts, tests, and history rather than this decision.

## Alternatives considered

- Retain specialist-specific durable notebooks: rejected because they create
  competing continuity models for work that already crosses the Wayfinder
  threshold.
- Copy specialist methods into Wayfinder: rejected because the coordinator
  would become large and drift from the native method owner.
- Add a generic specialist-result or handoff record: rejected because the map
  and native artifacts already carry the required pointers and next work.

## Reconsideration trigger

Reconsider if a specialist demonstrates a durable coordination need that cannot
be represented safely as a native artifact plus a concise Wayfinder pointer.
