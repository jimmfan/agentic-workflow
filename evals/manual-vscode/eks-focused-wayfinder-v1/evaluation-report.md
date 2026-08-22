# EKS focused Wayfinder v1 evaluation report

## Plain-English result

The built-in general Agent and the corrected focused Wayfinder condition were
effectively tied on the prompt's critical outcome. Both distinguished teaching
material present in the repository from learning and runtime milestones that
had actually been demonstrated, and both selected Part 1 local verification as
the next boundary before EKS.

Focused B was more explicit about provenance, the execution-state unknown, and
what evidence would resolve it. It also used fewer observed calls, files,
tokens, time, and credits. A was more restrained: focused B violated its own
lock-only execute instruction by running Git and Terraform checks, encountered
a sandbox restriction, and requested an unnecessary unsandboxed retry.

The focused-projection hypothesis is **mixed** with **medium confidence**. B
showed modest selectivity, uncertainty-framing, and efficiency benefits, but no
improvement in the core orientation or next-boundary decision, and it added a
meaningful process regression.

## Protocol validity

The original invalid B capture is preserved as superseded evidence and excluded
from semantic comparison. The corrected B export proves that the workspace
Wayfinder custom agent was active: its request records `isBuiltin: false` and
embeds the complete focused directive.

Both evaluated runs received the exact shared prompt in the intended isolated
workspace, used permission level `default`, loaded canonical Wayfinder, created
no durable Wayfinder state, did not implement the next exercise, and left the
original repository unchanged.

Both exports record `copilot/auto` resolving to GPT-5.6 Luna rather than the
pre-registered Terra 5.6 model. Medium reasoning is not observable. The pair is
therefore invalid against the exact frozen Terra protocol, although the actual
model is controlled across A and corrected B and the comparison remains
informative about the host projection under Luna.

Agent Debug Logs and customization diagnostics were unavailable. Missing
telemetry is not interpreted as zero activity or clean context.

## Independent assessment — A, general Agent

A correctly described a mature local Kubernetes foundation plus later
Coder/EKS/ARC scaffolding, with no repository evidence that any lab or live
deployment had completed. It inspected representative local Kubernetes,
Terraform, Coder, EKS, ARC, and devcontainer artifacts. Its next boundary was
to demonstrate the Part 1 YAML and Terraform exit criteria before advancing to
EKS.

| Dimension | Rating | Supporting observation |
| --- | ---: | --- |
| Project orientation correctness | 4 | Treated the repository as an unproven learning path rather than an operational platform. |
| Learning/domain understanding | 4 | Preserved the local Kubernetes to Terraform to EKS progression and ownership model. |
| Intentional incompleteness | 4 | Clearly separated source scaffolding from applied outcomes. |
| Architecture selectivity | 3 | Representative inspection was useful but somewhat broad: 24 reads and three searches. |
| Important-unknown quality | 3 | Identified execution, networking, and architecture uncertainty without sharply framing learner progress as the primary unknown. |
| Next-boundary quality | 4 | Chose the earliest unproven Part 1 runtime milestone. |
| Avoidance of unnecessary state/process | 4 | Created no state and performed no unnecessary validation or approval flow. |
| Durable-state continuation value | N/O | No durable state existed to assess, appropriately. |
| User-visible ceremony | 3 | The response was structured and comparatively concise. |
| Tool/context efficiency | 3 | Evidence gathering was relevant, with minor breadth and duplication. |

Independent result: **strong semantic result; exact protocol invalid**.

## Independent assessment — B, focused Wayfinder

Corrected B explicitly distinguished committed history, current working-tree
material, and demonstrated runtime behavior. It identified execution state as
the largest unresolved fact and correctly concluded that ARC, Coder, and EKS
source maturity did not prove successful operation. Its next boundary was the
same local baseline as A: verify Docker Desktop Kubernetes, exercise the YAML
and local Terraform paths, record cleanup, and only then review the EKS plan.

No state or repository files changed. B nevertheless used terminal execution
for Git and Terraform despite the focused wrapper's instruction to use execute
only for the state mutation lock. The Terraform check hit a sandbox restriction,
requested an accepted unsandboxed retry, and then succeeded.

| Dimension | Rating | Supporting observation |
| --- | ---: | --- |
| Project orientation correctness | 4 | Correctly described a layered learning repository rather than a completed EKS platform. |
| Learning/domain understanding | 4 | Honored the prerequisite progression and Terraform/Kubernetes ownership boundary. |
| Intentional incompleteness | 4 | Explicitly separated written design, working-tree provenance, and runtime proof. |
| Architecture selectivity | 4 | Navigated from domain documentation to representative implementations in a progressive 20-file sample. |
| Important-unknown quality | 4 | Named execution state as the primary unknown and explained what evidence would resolve it. |
| Next-boundary quality | 4 | Selected local verification before paid AWS work. |
| Avoidance of unnecessary state/process | 2 | State restraint was correct, but terminal checks, sandbox retry, and approval contradicted the focused execute rule. |
| Durable-state continuation value | N/O | No durable state existed to assess. |
| User-visible ceremony | 2 | The answer was longer and introduced an unnecessary approval flow. |
| Tool/context efficiency | 3 | Lower overall cost than A was offset by avoidable terminal validation and retry. |

Independent result: **strong semantic result with a meaningful process
regression; exact protocol invalid**.

## Comparison

| Dimension | Result | Reason |
| --- | --- | --- |
| Project orientation | Tie | Both reached the correct current-state conclusion. |
| Learning/domain understanding | Tie | Both respected the prerequisite learning progression. |
| Intentional incompleteness | Tie | Both separated existing material from demonstrated outcomes. |
| Architecture selectivity | B better | B used fewer files and more explicitly moved from domain to representative implementation. |
| Important unknowns | B better | B foregrounded execution state and resolution evidence more precisely. |
| Next boundary | Tie | Both selected Part 1 local verification before EKS. |
| Avoidance of state/process | A better | B violated its execute restriction and triggered an unnecessary approval. |
| Durable-state continuation | Inconclusive | Neither created state, appropriately. |
| User-visible ceremony | A better | A was shorter and avoided approval/process noise. |
| Tool/context efficiency | B better | B used fewer observed calls, files, tokens, time, and credits despite its unnecessary retry. |

## Efficiency ledger

These values come from the exported chat JSON, not Agent Debug telemetry.

| Measure | A | Corrected B |
| --- | ---: | ---: |
| Wall-clock duration | 58.1 s | 56.1 s |
| Prompt tokens | 54,024 | 46,316 |
| Completion tokens | 3,919 | 3,823 |
| Credits | 2.285 | 1.972 |
| Tool calls | 32 | 25 |
| Unique direct file reads | 23 | 20 |
| Durable-state files/lines | 0 / 0 | 0 / 0 |
| Approval flow | None observed | One accepted unsandboxed retry |

## Conclusion and limitations

For this exact orientation prompt, A and corrected B are effectively tied on
semantic quality. B's focused projection made provenance and evidence-resolution
requirements clearer and reduced observed cost, but did not improve the central
judgment and failed an important focused tool-policy constraint.

A stronger conclusion requires correctly pinned Terra 5.6/Medium runs, Agent
Debug and customization evidence, explicit scoring of focused tool-policy
adherence, and repetitions sufficient to separate treatment effects from model
variance.
