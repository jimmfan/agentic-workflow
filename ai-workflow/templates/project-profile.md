# Project profile

## Purpose and success

Describe the project, its users, and observable success.

## Technology and architecture

List verified technologies, important components, and their relationships.

## Important paths

Map the few directories an agent usually needs. Name the project-owned durable
specification location and local ticket destination or accepted native tracker,
or state that each has not been established.

## Terminology

Define project-specific terms. Use `None` when there are none.

## Constraints and policy

Record security, organizational, compatibility, approval, and scope constraints.

## Delivery workflow

Describe how a change normally moves from development through release. State any
plan-approval policy, when proportional independent review is required, and who
may accept a review limitation. Review does not replace executable Verification.

## Commands

Copy a complete entry from `ai-workflow/contracts/project-profile.md` for each
real command or manual check. If none are configured, write:

`No project checks are configured. Report verification as blocked; do not invent commands.`

## Debugging model

Describe the project's request/data/control path and useful evidence at each
layer. Use `None` until verified.

## Decision considerations

List domain-specific tradeoffs and policies. Use `None` until verified.

## Profile maintenance

- Owner: Project maintainers
- Last reviewed: YYYY-MM-DD
- Becomes stale when: Architecture, toolchain, delivery, or policy changes.
- Conflict behavior: Verify against source and live evidence, report the conflict,
  and update this profile before relying on the disputed field.
