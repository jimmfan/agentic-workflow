# Independent audit of vanilla Codebase Design

This is an instruction audit of the pinned v1.2.3 files, not an audit of the
underlying design philosophy and not a live-model behavior claim.

## Strongest ideas

### Useful principles

- Judge an abstraction by leverage for callers and locality for maintainers,
  not by implementation line count.
- Treat an interface as all caller obligations—including invariants, ordering,
  errors, configuration, and performance—not just a type signature.
- Separate the question of where a seam belongs from the implementation behind
  it.
- Prefer a coherent behavioral test surface that survives internal refactors.
- Inject genuinely variable or external dependencies and keep transport details
  out of core logic.

### Useful heuristics

- The deletion test is an effective prompt for spotting wrappers that only move
  complexity into callers or add navigation cost.
- Fewer entry points and simpler parameters often improve usability, provided
  behavioral state space is considered separately.
- Repeated ordering, validation, and error-handling knowledge across callers is
  evidence that a deeper operation may improve locality.
- Comparing more than one interface design can expose assumptions in a
  consequential, genuinely open design choice.

## Highest-risk wording

### Dangerous absolutes

- `Use these terms exactly` and the prohibition on `component`, `service`,
  `API`, and `boundary` can overwrite established project or domain language.
  Vocabulary consistency is valuable inside a review method, but it does not
  grant authority to rename canonical concepts.
- `Use this language and these principles wherever code is being designed or
  restructured` makes a specialist lens effectively universal and encourages
  architecture review during routine implementation.
- `In-process ... Always deepenable — merge the modules` treats technical
  mergeability as architectural evidence. It ignores cohesion, ownership,
  independent evolution, security, failure isolation, domain semantics, and
  cognitive locality.
- `Old unit tests ... become waste ... delete them` turns a refactoring goal
  into a deletion rule without requiring equivalent behavioral coverage or
  diagnostic quality. Focused tests for parsing, algorithms, invariants,
  concurrency, security, or failure semantics can remain valuable below a
  higher-level interface.
- `A Module has exactly one Interface` does not generalize to modules that
  intentionally present distinct surfaces to different caller groups.

### Context-dependent recommendations stated too strongly

- `One adapter means a hypothetical seam` is a useful anti-speculation prompt,
  but adapter count is not a sufficient test. A single production adapter can
  sit at a real ownership, protocol, trust, lifecycle, or deployment seam; a
  mock created only for tests does not automatically prove a meaningful seam.
- `If you want to test past the interface, the module is probably the wrong
  shape` is a good smell detector, but some concentrated internal hazards are
  cheaper and clearer to test directly.
- `Fewer methods = fewer tests needed` conflates surface size with behavioral
  state space. One method can contain many consequential cases.
- `Return results, don't produce side effects` is useful for isolating
  computation, but commands and transactional operations legitimately have
  side effects; the important issue is making outcomes and failure semantics
  observable.
- Availability of a local stand-in does not by itself justify hiding a seam.
  Stand-in fidelity and the dependency's ownership/contract still matter.

## Likely induced behavior

The wording strongly focuses attention on caller knowledge, pass-through
delegation, duplicated orchestration, and test surfaces. That should improve
reviews of genuinely layered code such as Scenario A. The same salience can
produce false positives: a reviewer is explicitly instructed to merge all
in-process modules, use a foreign glossary, and delete lower-level tests after
deepening. Invoking the skill more frequently therefore increases the chance
that these absolutes dominate weaker repository evidence.

The instructions can also replace one abstraction with another while claiming
simplification. A reviewer may remove named domain modules and introduce a
single large “deep module,” injected ports, and adapters. The count of files or
types falls, while callers now depend on a broader operation with more combined
reasons to change.

## Effects on adjacent concerns

- **Domain Modeling:** mandatory Codebase Design vocabulary conflicts with
  ubiquitous project language. Domain Modeling should own canonical term and
  domain-boundary changes; Codebase Design can describe leverage without
  renaming those concepts.
- **Discovery:** Design It Twice overlaps alternative generation. Discovery is
  the better owner when the consequential question is a choice among viable
  architectures; Codebase Design can supply evaluation criteria.
- **Wayfinder:** Codebase Design can reduce territory when evidence shows
  pass-through layers or duplicated caller knowledge. It can also add a second
  architecture-analysis layer to already complex territory if selected merely
  because many modules exist.
- **Implementation:** a settled implementation scope does not authorize a
  repository-wide deepening refactor. The skill must remain inside the accepted
  boundary unless a new decision is escalated.
- **Project authority:** established terminology, ownership boundaries, public
  compatibility, and deletion of test coverage are project decisions or
  evidence questions, not consequences of skill invocation.
- **Design It Twice:** the unconditional 3+ sub-agent pattern is disproportionate
  for obvious consolidation, low-risk internal interfaces, or tasks where the
  user did not authorize extra agents. “Radically different” designs can reward
  novelty over plausible fit and increase synthesis work.

## Classification summary

- Useful principles: leverage, locality, broad interface obligations, explicit
  seam placement, behavior-oriented tests.
- Useful heuristics: deletion test, smaller caller surface, dependency
  injection, alternative comparison.
- Context-dependent: adapter-count test, result-over-side-effect preference,
  interface-only testing, local stand-ins, module consolidation.
- Dangerous absolutes: mandatory glossary, all in-process modules must merge,
  lower-level tests become waste, exactly one interface, universal use, and
  unconditional 3+ agent expansion.
