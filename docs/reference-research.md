# Matt Pocock skill reference research

Inspected read-only on 2026-08-12. A live `git ls-remote` confirmed that current
`main` remained
[`84fdeffd12f2ee307994d1eb6feb48173b6e0502`](https://github.com/mattpocock/skills/commit/84fdeffd12f2ee307994d1eb6feb48173b6e0502),
committed 2026-08-06 at 20:49:51+01:00. The source declares bundle/plugin
version 1.2.3; the immutable SHA, not the release label, is the audited identity.
No audited skill was installed, activated, executed, or copied. The authoritative
repository is [mattpocock/skills](https://github.com/mattpocock/skills), licensed
under [MIT](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/LICENSE),
copyright 2026 Matt Pocock.

## Wayfinder

Older references call this skill `decision-mapping`; the current source and
documentation use `wayfinder` under `skills/engineering/wayfinder`.

Relevant immutable paths:

- [skill instructions](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/engineering/wayfinder/SKILL.md)
- [OpenAI invocation policy](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/engineering/wayfinder/agents/openai.yaml)
- [human documentation](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/docs/engineering/wayfinder.md)
- [setup skill](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/engineering/setup-matt-pocock-skills/SKILL.md)
- [local tracker adapter](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md)

Wayfinder is user-invoked with `/wayfinder`; both
`disable-model-invocation: true` and the OpenAI manifest's
`allow_implicit_invocation: false` prohibit silent router invocation. Its trigger
is narrow: a foggy effort too large for one agent session, not every unresolved
choice. Chart mode takes a loose idea and destination. Work mode takes a map URL
or number and optionally a ticket.

Its canonical state is one issue-tracker map plus child decision tickets. The
map is a low-detail index; ticket comments hold resolutions. With no configured
tracker it falls back to local Markdown under `.scratch/<effort>/`. Therefore a
real invocation can mutate an external tracker or the repository and must use
the framework's normal authorization boundary. Resume is another explicit
`/wayfinder <map>` invocation. A cleared map hands to specification and build
planning; Wayfinder does not normally implement the product.

This framework adopts the useful principles—externalize durable uncertainty,
load a concise index, avoid duplicated evidence, and separate decisions from
implementation—but keeps ordinary decisions in the much smaller local
`workflow-discovery`. An installed upstream Wayfinder remains an explicit opt-in
for its actual multi-session use case. Its map stays authoritative; framework
state records only the origin and return target, not a duplicate ticket system.
If it is explicitly requested but unavailable, the router says so and offers
local Discovery.

## Teach

Matt Pocock's [Teach overview](https://www.aihero.dev/skills-teach) points to the
same repository. `teach` is the skill ID and `/teach` is its explicit invocation.

Relevant immutable paths:

- [skill instructions](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/productivity/teach/SKILL.md)
- [OpenAI invocation policy](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/productivity/teach/agents/openai.yaml)
- [mission format](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/productivity/teach/MISSION-FORMAT.md)
- [resources format](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/productivity/teach/RESOURCES-FORMAT.md)
- [learning-record format](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/productivity/teach/LEARNING-RECORD-FORMAT.md)
- [human documentation](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/docs/productivity/teach.md)
- [handoff skill](https://github.com/mattpocock/skills/blob/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/productivity/handoff/SKILL.md)

Teach is also explicit-only. Its documented purpose is a multi-session learning
project, not a one-off explanation. Upstream recommends one topic in a dedicated
repository outside the engineering project. The workspace owns `MISSION.md`,
`RESOURCES.md`, HTML lessons and references, reusable assets, learning records,
and notes; files, not chat, provide continuity. Each lesson is another explicit
invocation.

The mission supplies motivation, success, and constraints. Existing learning
records help select the next lesson, but current Teach has no initial assessment
step and does not guarantee that prior knowledge will be elicited. It builds
mental models and practice evidence; it does not make architecture decisions,
implement engineering work, certify mastery, or determine an automatic exit.
Upstream `/handoff` writes a compact file to the operating-system temporary
directory; it is a bridge, not durable project state, and Teach defines no
automatic return event.

This framework uses `workflow-teach` for bounded project-grounded knowledge gaps
and adds the exact Discovery resume pointer that upstream does not provide. An
installed upstream Teach remains an explicit opt-in when learning itself is the
multi-session project. Its course artifacts stay authoritative in the dedicated
workspace; local state stores only the interrupted workflow and return target.
If it is explicitly requested but unavailable, the router says so and offers
the local workflow.

## Engineering workflow comparison

The same immutable revision was used to audit `to-spec`, `to-tickets`,
`diagnosing-bugs`, `tdd`, `code-review`, `implement`, and
`writing-for-agents`. This was a contract comparison, not an installation or
runtime dependency. The approved v0 dispositions are:

| Upstream skill | Disposition in this framework |
|---|---|
| `to-spec` | Excluded as a route. The project-owned specification transition already preserves accepted decisions, canonical placement, authorization, and durable links without a second specification owner. |
| `to-tickets` | Its dependency-aware, independently completable ticket mechanics inform `workflow-decomposition`. A separately installed copy may be explicitly selected when its native tracker should be canonical; full ticket bodies are never mirrored into `IMP` state. |
| `diagnosing-bugs` | Does not replace `workflow-debugging`. Its exact-symptom feedback, minimization, explicit hypotheses, targeted instrumentation, and validation-seam mechanics strengthen the broader local workflow, which also supports cloud/infrastructure proxies and diagnosis-only scope. |
| `tdd` | Not a route or universal requirement. Test-first vertical slices are optional inside Implementation only when a stable observable seam and independently known expected behavior provide real signal; configured declarative validation remains valid elsewhere. |
| `code-review` | May be explicitly selected for its committed fixed-point Standards/Spec contract. Local `workflow-review` remains the proportional owner of correctness, security, validation gaps, unintended scope, and parent-confirmed disposition. |
| `implement` | Excluded as a route because it overlaps the canonical Implementation and Verification ownership without replacing their project profile, authorization, state, or evidence contracts. |
| `writing-for-agents` | Applied as authoring guidance: concise router, precise trigger descriptions, progressive disclosure, reduced behavioral duplication, human-facing rationale, and explicit completion criteria. It is not invoked as an engineering stage. |

These decisions preserve upstream-native artifacts when explicitly used while
keeping the local specification, Debugging, Implementation, Verification, and
durable-state contracts canonical. No new agent runtime is introduced.

## License and attribution consequence

The local workflows are independently written minimal contracts, not copies or
substantial portions of the audited upstream skills. Attribution is retained
because they are meaningful design influences. Any future copied source content must
carry the upstream MIT copyright and permission notice.
