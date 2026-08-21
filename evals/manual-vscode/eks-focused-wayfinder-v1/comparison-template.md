# EKS focused Wayfinder blind-style comparison template

Use this only after both runs and their artifacts are frozen. Review each
condition independently before revealing or using the other condition's
assessment. Treatment labels do not earn credit.

## Evidence hierarchy

Prefer, in order:

1. frozen repository source and post-run repository artifacts;
2. Agent Debug events, tool payloads, and recorded metrics;
3. exported chat content and complete final response;
4. operator notes and screenshots;
5. agent self-report when stronger evidence is unavailable.

Mark an observation `not available` rather than inferring it. Distinguish a
wrong claim from an unverified claim and a deliberately unresolved question.

## Rating scale

Use the scale per dimension; do not calculate an aggregate score.

| Rating | Meaning |
| --- | --- |
| 4 — strong | Correct, specific, well-supported, and materially useful. |
| 3 — adequate | Mostly correct and useful, with minor omissions or overhead. |
| 2 — mixed | Some useful behavior, but important gaps, weak support, or avoidable cost. |
| 1 — weak | Materially misleading, incomplete, irrelevant, or process-heavy. |
| 0 — failed | Contradicted by the repository, unsafe, or did not perform the requested orientation. |
| N/O | Not observable from the captured evidence. |

## Protocol validity

Complete before semantic grading.

| Check | Condition X | Condition Y |
| --- | --- | --- |
| Correct isolated workspace |  |  |
| Fresh empty chat |  |  |
| Exact prompt only |  |  |
| `Terra 5.6` |  |  |
| `Medium` reasoning |  |  |
| Same permission policy |  |  |
| Local memory tool disabled |  |  |
| Copilot Memory disabled |  |  |
| No user/profile customization loaded |  |  |
| Organization customization disabled |  |  |
| Cross-device session history sync disabled |  |  |
| Intended selected agent |  |  |
| No next-exercise implementation |  |  |
| Original repository unchanged |  |  |
| Result status: valid / qualified / invalid |  |  |

Record every deviation and decide whether it invalidates only one metric, one
condition, or the whole comparison.

## Independent assessment — Condition X

### Evidence inventory

- Final response:
- Durable state:
- Files read/searched:
- Tool calls:
- Elapsed time:
- Token/usage data:
- Route reported:
- Errors, approvals, or corrections:
- Unexpected repository changes:
- Memory/preference/customization audit:

### Dimension review

| Dimension | Rating | Exact supporting or contradicting evidence | Interpretation |
| --- | ---: | --- | --- |
| Correctness of project orientation |  |  |  |
| Understanding of actual learning/domain state |  |  |  |
| Honest treatment of intentional incompleteness |  |  |  |
| Relevance/selectivity of architecture inspection |  |  |  |
| Quality of important unknowns |  |  |  |
| Quality of proposed next boundary |  |  |  |
| Avoidance of unnecessary state/process creation |  |  |  |
| Durable-state usefulness for a fresh continuation |  |  |  |
| User-visible verbosity/ceremony |  |  |  |
| Tool/context efficiency |  |  |  |

### Condition X conclusion

- What it did well:
- Material errors or omissions:
- Whether its state would help a fresh continuation, and why:
- Whether the result is positive, negative, mixed, or inconclusive on its own:

## Independent assessment — Condition Y

Do not consult Condition X's ratings while completing this section.

### Evidence inventory

- Final response:
- Durable state:
- Files read/searched:
- Tool calls:
- Elapsed time:
- Token/usage data:
- Route reported:
- Errors, approvals, or corrections:
- Unexpected repository changes:
- Memory/preference/customization audit:

### Dimension review

| Dimension | Rating | Exact supporting or contradicting evidence | Interpretation |
| --- | ---: | --- | --- |
| Correctness of project orientation |  |  |  |
| Understanding of actual learning/domain state |  |  |  |
| Honest treatment of intentional incompleteness |  |  |  |
| Relevance/selectivity of architecture inspection |  |  |  |
| Quality of important unknowns |  |  |  |
| Quality of proposed next boundary |  |  |  |
| Avoidance of unnecessary state/process creation |  |  |  |
| Durable-state usefulness for a fresh continuation |  |  |  |
| User-visible verbosity/ceremony |  |  |  |
| Tool/context efficiency |  |  |  |

### Condition Y conclusion

- What it did well:
- Material errors or omissions:
- Whether its state would help a fresh continuation, and why:
- Whether the result is positive, negative, mixed, or inconclusive on its own:

## Comparison after independent review

Reveal the treatment labels only now.

| Dimension | A assessment | B assessment | Better / tie / inconclusive | Why the evidence supports that result |
| --- | --- | --- | --- | --- |
| Correctness of project orientation |  |  |  |  |
| Understanding of actual learning/domain state |  |  |  |  |
| Honest treatment of intentional incompleteness |  |  |  |  |
| Relevance/selectivity of architecture inspection |  |  |  |  |
| Quality of important unknowns |  |  |  |  |
| Quality of proposed next boundary |  |  |  |  |
| Avoidance of unnecessary state/process creation |  |  |  |  |
| Durable-state usefulness for a fresh continuation |  |  |  |  |
| User-visible verbosity/ceremony |  |  |  |  |
| Tool/context efficiency |  |  |  |  |

## Efficiency ledger

| Measure | A | B | Limitation |
| --- | ---: | ---: | --- |
| Wall-clock duration |  |  |  |
| Input tokens |  |  |  |
| Output tokens |  |  |  |
| Reasoning tokens |  |  |  |
| AI credits/cost, if shown |  |  |  |
| Total tool calls |  |  |  |
| Read/search tool calls |  |  |  |
| Unique repository files read |  |  |  |
| Architecture files read |  |  |  |
| Irrelevant files read |  |  |  |
| Durable files created/modified |  |  |  |
| Durable-state lines |  |  |  |
| Non-state files changed |  |  |  |
| Errors/corrections |  |  |  |

Lower cost is favorable only when correctness, honesty, and continuation value
are not materially worse. More state is favorable only when it reduces future
reconstruction or prevents a consequential mistake.

## Final experimental conclusion

- Plain-English result:
- Does B improve project orientation over A?
- Does B improve durable coordination over A?
- What benefit, if any, is attributable to the focused host/agent condition?
- What overhead or regression accompanies that benefit?
- Important confounders or missing evidence:
- Result classification: supports hypothesis / does not support hypothesis /
  mixed / inconclusive
- Most useful next action, without changing Agentic Workflow during this pair:
