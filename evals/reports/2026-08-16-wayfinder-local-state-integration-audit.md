# Wayfinder local-state integration audit

## Pre-implementation semantic audit

| Concern | Current effective behavior | Evidence/path | Pass/fail | Required fix |
| --- | --- | --- | --- | --- |
| Canonical storage | Root routing and the state contract require `.ai-workflow-state/wayfinder/<effort>/`, but the selected provider body calls a tracker issue canonical and directs setup or `.scratch/` fallback. | `AGENTS.md`; `.ai-workflow/routing.md`; `.ai-workflow/contracts/wayfinder-state.md`; `.agents/skills/wayfinder/SKILL.md`; `issue-tracker-local.md` | Fail | Put an authoritative local-mode adapter in the loaded provider body; disable tracker mechanics in that mode. |
| U/D/T ontology | The local contract defines U# questions, D# durable choices, and T# executable work. The provider calls every decision/investigation a ticket, which encourages writing questions as T#. | Wayfinder state contract; provider `Tickets` and `Ticket Types` sections | Fail | Map decision/research/prototype/grilling questions to U#, create D# only for durable decisions, and use T# only for concrete work. |
| Method versus mechanics | Destination, low-resolution map, fog, progressive loading, and dependency-derived frontier are compatible, but they are interleaved with issue labels, assignment, comments, closing, and tracker-native blocking. | Pinned Wayfinder v1.2.3 body and local tracker setup document | Fail | Preserve the method and explicitly replace only physical storage/lifecycle mechanics. |
| Dynamic escalation | Routing permits Wayfinder to take durable coordination ownership mid-Debugging or mid-Discovery, but the provider says charting stops the session and planning normally excludes doing. | `.ai-workflow/routing.md`; provider `Plan, don't do` and `Invocation` sections | Fail | State that specialized work can continue inside the map and that Wayfinder does not erase a useful active capability. |
| Grilling and Domain Modeling | Upstream always invokes both while charting; local routing neither mandates nor rejects them. This makes effective behavior accidental. | Provider `Chart the map`; Grilling and Domain Modeling skill bodies | Fail | Require them only when destination/domain ambiguity genuinely needs HITL/domain clarification; forbid ceremonial invocation. |
| Read-only boundary | Root/routing prohibit state writes, while the provider's chart flow directs immediate map/ticket creation. | Root/routing/state contract versus provider `Chart the map` | Fail | Restate read-only precedence inside the selected skill; allow ephemeral reasoning only. |
| Re-entry and evidence precedence | Local contracts correctly load `map.md` first, zoom selectively, and prefer live/source evidence, but the provider does not know the local children or reconciliation rule. | Wayfinder and durable-state contracts; provider `Work through the map` | Fail | Put progressive local loading and explicit stale/conflict reconciliation in the adapter. |
| Lifecycle ownership | Core lifecycle already treats `.ai-workflow-state/` as opaque project data. Provider adaptation recognizes only metadata, so it cannot prove a body adaptation is safe. | `lifecycle.py`; `providers.py`; lifecycle tests | Partial | Fingerprint the pinned method body, adapt transactionally, and fail closed on unknown or modified content. |
| Activation/load behavior | Metadata descriptions control consideration, but Codex loads the full `SKILL.md` after selection; same-named skills are not merged. | Official Codex “Build skills” documentation | Fail | Adapt the selected provider body itself rather than relying on metadata, a duplicate wrapper, or an unreferenced contract. |

## Compatibility mapping

| Upstream concept | Agentic Workflow local representation | Owner | Lifecycle |
| --- | --- | --- | --- |
| Destination and low-resolution map | `map.md` headings and concise links/gists | Local Wayfinder effort | Created only when selected and writes are authorized; map is the re-entry point. |
| Fog of war | `map.md` → `Not yet specified` | Local Wayfinder effort | Remains vague until a consequential question is sharp enough for U#. |
| Decision/research/prototype/grilling ticket | U# with a resolution mode and evidence | Local Wayfinder effort; supporting capability owns its native evidence artifact only | Resolve with evidence; create/link D# only when a durable choice exists. |
| Upstream task ticket | T# only when the prerequisite is genuinely executable work, linked to the U# it unblocks | Local Wayfinder effort | Ready/blocked/in-progress/done according to actual work. |
| Resolved durable choice | D# plus a concise `Decisions so far` map link | Local Wayfinder effort/project decision | Update the same D# with a change note when evidence changes it. |
| Clear follow-on implementation | T# when decomposition adds value; otherwise direct coherent implementation | Local Wayfinder effort until consumed by Implementation | Implementation loads only the relevant T#/D#/U# context. |
| Labels, assignment, comments, issue close, tracker blocking | No local equivalent; status/dependency lines and collision-safe Markdown writes replace only needed mechanics | Not active in local mode | Never provision or mutate an external tracker solely for local Wayfinder. |

## Post-fix semantic audit

Gate result: **Pass.** The effective local-mode instructions are now coherent
enough to permit the smallest long-lived smoke. Green tests are supporting
evidence, not the reason for this verdict.

| Concern | Effective behavior after the fix | Evidence/path | Pass/fail |
| --- | --- | --- | --- |
| Instruction precedence | A leading, delimited local-mode block says that it and the local contracts override incompatible tracker mechanics in the untouched upstream body. When the contract is absent, upstream behavior is restored. | `.agents/skills/wayfinder/SKILL.md`; `docs/decisions/0020-own-the-declared-provider-projection.md` | Pass |
| Canonical storage | The only local Wayfinder representation is `.ai-workflow-state/wayfinder/<effort>/`; `.scratch/`, external tracker copies, and a global active file are forbidden. | Root policy; routing contract; Wayfinder state contract; adapter block | Pass |
| U/D/T ontology | Sharp questions use U#, durable choices use D#, and concrete executable outcomes use T#. Resolution does not force a U# -> D# -> T# pipeline. | Wayfinder state contract, `Identifiers and relationships`; adapter block; routing scenarios | Pass |
| Method versus mechanics | Destination, low-resolution orientation, fog, incremental uncertainty reduction, progressive detail, and a dependency-derived frontier remain upstream-owned. Tracker setup, assignment, comments, closing, and tracker-native blocking are inactive only in local mode. | Adapter block followed by byte-preserved upstream method; provider declaration body fingerprint | Pass |
| Dynamic escalation and composition | Wayfinder may assume durable coordination ownership mid-task without erasing useful Debugging, Research, Prototype, Implementation, or human clarification work. Supporting capabilities link evidence into the map rather than creating a second owner. | `.ai-workflow/routing.md`; Wayfinder state contract, `Workflow boundaries`; adapter block | Pass |
| Grilling and Domain Modeling | Both are conditional on real human-preference, destination, language, or ownership ambiguity. Neither is mandatory ceremony. Grilling cannot invent the human side. | Routing contract; Wayfinder state contract; adapter block | Pass |
| Read-only boundary | Read-only work may use the reasoning method but cannot create or update state. The adapter now loads the Wayfinder contract on selection and defers the general durable-state contract until an authorized write. | Root load gate; Wayfinder state contract, `Ownership and locations`; adapter block; lifecycle loading-upgrade test | Pass |
| Re-entry, progressive loading, and evidence precedence | Route first, then load the relevant map, then only needed children. Live/source evidence wins over stale state; concurrent evidence is preserved and reconciled explicitly. | Root load gate; durable-state contract; Wayfinder state contract, `Progressive loading`; adapter block | Pass |
| Lifecycle ownership | Install/update adapt only a recognized pinned provider body and metadata. Unknown or modified content fails closed without partial writes. Lifecycle treats all `.ai-workflow-state/` content as opaque project data. | `providers.py`; provider schema; lifecycle tests for fresh, idempotent, recognized upgrade, incompatible content, status, remove, and state preservation | Pass |
| Activation/load behavior | Codex can implicitly select the adapted provider, and once selected loads the full `SKILL.md`; a same-named wrapper is not needed. | Provider declaration and projected metadata; [official Codex skill documentation](https://learn.chatgpt.com/docs/build-skills.md) | Pass |
| Payload/projection agreement | Installed routing, provider declaration, and state contracts match their payload sources; the projected adapter is ready and its upstream remainder matches the declared SHA-256 fingerprint. | Payload/installed byte comparison; `providers.py status`; adapter integrity check | Pass |

The upstream tracker language intentionally remains below the adapter and still
matches the pinned provider body. It is not a second effective local contract:
the leading block explicitly disables those mechanics when the local Wayfinder
contract exists. Preserving the body is what keeps the integration narrow and
makes upstream drift detectable.

## Duplication and progressive-loading audit

The current instructions are semantically consistent, but several invariants
are restated more often than necessary. Repetition is most expensive on
Wayfinder routes because those routes load the router, the local state contract,
and the full provider method.

| Invariant | Current repetition | One authoritative home | Smallest safe deduplication |
| --- | --- | --- | --- |
| User authority, read-only boundaries, truthful execution, and preservation of unrelated work | `AGENTS.md`, routing, durable-state, Wayfinder-state, and the adapter | `AGENTS.md` for the universal rule | Keep the root invariant. In later-loaded files, state only the local consequence that is necessary to defeat a conflicting provider instruction, then point back to the root rule. |
| Dominant route, dynamic escalation, opt-out, and supporting-capability composition | `AGENTS.md`, routing, Wayfinder-state, and the adapter | `routing.md` | Keep only a compact routing/load summary in `AGENTS.md`. Remove route-selection prose from the state contract and adapter; retain an explicit adapter sentence that Agentic Workflow routing controls local-mode selection. |
| General durable locations, source precedence, conflict handling, collision safety, and no global active index | `AGENTS.md`, routing, durable-state, Wayfinder-state, and the adapter | `durable-state.md` | Let Wayfinder-state define only per-effort exceptions and link to the general conflict/write rules. Keep the adapter's explicit prohibition on the alternate stores named by upstream instructions. |
| Local path, U/D/T meaning, authoring shapes, lifecycle non-interference, map-first re-entry, and progressive child loading | routing, durable-state, Wayfinder-state, and the adapter | `wayfinder-state.md` | Reduce routing and durable-state to pointers. Shorten the adapter to precedence plus the minimum incompatible-mechanics override, then direct all representation details to the Wayfinder contract. |
| Upstream destination/fog/frontier method and local override of tracker mechanics | Wayfinder-state, adapter, and the upstream provider body | Upstream provider body for the method; adapter for override precedence | Remove the method summary from the state contract and adapter. Keep the adapter's delimited authority statement and its explicit list of disabled tracker behaviors. |
| Conditional Grilling/Domain Modeling and continued specialized work | routing, Wayfinder-state, and adapter | `routing.md` | Keep composition policy in routing. The adapter needs only to neutralize upstream's unconditional invocations and stop-work default; the state contract can link to routing. |

### Approximate loaded instruction bytes

These counts use the current source repository's full `AGENTS.md` (17,801
bytes, of which 3,454 bytes are the installed managed region and 14,346 bytes
are source-repository policy). They count complete instruction files required by
the route and the selected skill. They exclude system/app prompts, user text,
project artifacts, automatically indexed skill descriptions, and the declarative
provider registry; reading that entire registry rather than selecting its
Wayfinder entry adds 5,891 bytes.

| Path | At audit start | After the applied loading fix | After the recommended deferred deduplication |
| --- | ---: | ---: | ---: |
| Direct | 17,801 | 17,801 | about 17,800 |
| Read-only Debugging | 34,904 | 34,904 | about 32,600 |
| Wayfinder read-only | 65,925 | 55,608 | about 50,800 |
| Wayfinder durable write | 65,925 | 65,977 | about 60,400 |

The audit-start adapter conservatively loaded the 10,369-byte durable contract
even for read-only Wayfinder. The applied fix removes that unnecessary load;
the write path is 52 bytes larger because the new gate is more explicit. A
Debugging session that creates or resumes a DBG record would also load the
durable contract, adding 10,369 bytes to the read-only Debugging row.

The deferred estimates assume roughly 10.3 KB for routing, 9.6 KB for the
general durable contract, 9.2 KB for the Wayfinder state contract, and 13.5 KB
for the adapted provider skill, while leaving the always-loaded root and the
4,463-byte Debugging skill unchanged. They are design estimates, not measured
post-change values.

### Deduplication disposition

Only the read-only/durable-write load gate was changed in this fix. It is both
clearly safe and directly relevant to progressive loading, and the lifecycle
recognizes and transactionally upgrades the immediately preceding exact adapter
form. The broader deduplication is recommended as a separate, reviewable
contract cleanup after this Wayfinder evaluation. Doing it now would widen the
behavioral surface just before the smoke and would make any evaluation change
harder to attribute.
