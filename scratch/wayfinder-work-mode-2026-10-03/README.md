# Wayfinder Work Mode diagnostic — October 3, 2026

This scratch branch publishes the completed diagnostic so another agent can review it outside ChatGPT.
The tested framework revision was `deb91942ac45373111a6bc615b359b2bbb230a68` (0.41.2).
Publication adds archival results only; it changes no framework instructions, package content, version or real effort maps.

**Observed saved-state and public-response outcomes: PASS across 36 subject turns.**
**Overall procedural, context-pressure and subject-compaction conformance: INCONCLUSIVE.**
No observed failure with a concrete consequence was found.
This single trajectory does not establish historical improvement, statistical reliability, native Codex/Claude behavior or state-contract split safety.

## Start here

- [Full report](REPORT.txt): setup, outcomes, coverage limits and remaining native-host prerequisites.
- [Independent assessment](grading.txt): the 36-turn matrix and evidence-grounded findings.
- [Machine-readable grades](grades.json): scoped per-turn outcomes and inconclusive checks.
- [Public transcript](public-transcript.txt): exact submitted tasks and returned public responses.
- [Exact evidence ZIP](Wayfinder-Work-Mode-evidence-2026-10-03.zip): protocol, frozen inputs, fixtures, snapshots, audit scripts, reader provenance and grading.
- [SHA-256 checksums](SHA256SUMS): integrity of the five original published files.

## Review with another agent

Give the agent this directory URL, or clone this branch into its workspace.
Have it read the report and independent assessment before inspecting individual requests and snapshots in the ZIP.
For an evidence review, keep the artifacts unchanged and do not rerun subjects or treat the archive as authorization for new live tests.

The approved run comprised one 31-turn writer, two two-turn controls, one files-only reader and one independent grading task.
It used inherited Work Mode agents with manually supplied installed skill descriptions and cooperative filesystem scope.
The exact model and reasoning effort were unavailable.
Twelve historical context batches totaling 456,275 UTF-8 bytes were staged as current-turn files; complete consumption and actual context occupancy were unobserved.
No subject compaction event or complete independent child tool trace was exposed.
The early stale-count repair reduced coverage of the originally planned turn-4 trigger.

## Reading paths and extracting evidence

Absolute `/workspace/scratch/...` paths and `sandbox:` links in exact captures identify the original session.
They are historical references, not portable external links.
Use the relative paths inside the extracted bundle to locate the corresponding evidence.
For example, `turns/subject-01/31/after.zip::docs/export-plan.md` in the grading report means member `docs/export-plan.md` in the bundle's `evidence/turns/subject-01/31/after.zip`.

The outer ZIP includes 64 relative symlinks for installed consumer skills.
Use an extractor that preserves symlinks for faithful whole-consumer inspection.
Captured files remain exact; no historical paths or conclusions were rewritten for publication.
Scripts containing original setup dependencies are evidence, not a one-command portable rerun adapter.

Statements that the source checkout was clean and remote main matched the pinned commit are observations at diagnostic completion.
They are not claims that publication left this scratch branch without a new result commit.

The full evidence ZIP is retained on this explicitly requested scratch branch for sharing.
It is outside the repository's compact evaluation result directories, and this branch is not intended to merge the raw archive into main.
