# Volunteer observing-card handoff

Use [the delivery map](.project-efforts/observing-card-delivery/map.md) first when resuming; it maintains readiness and remaining acceptance work. [Delivery guidance](docs/delivery.md) establishes the volunteer print trial and project owner alignment review.

## Prepared input and local evidence

[docs/observing-cards.csv](docs/observing-cards.csv) is the prepared CSV from the unchanged catalog. Its parsed rows are:

| name | magnitude |
| --- | --- |
| Alpha, Test | 4.1 |
| Polaris | 2.0 |
| Sirius | -1.46 |

The exporter sorts names using `casefold()` on a new list, preserving input order among equal keys. Python's CSV writer escapes commas, quotes and line breaks and uses CRLF record endings. Supplied magnitudes are passed directly to the writer without rounding or replacement; supplied strings keep their formatting.

On 2026-10-03, `python verify.py` exited 0 with `{"check": "catalog-local", "passed": true, "errors": []}`. Additional local round-trip assertions passed for quotes, commas, embedded CR/LF, magnitude strings with trailing zeros, stable case-insensitive ties, empty input and unchanged input values. These checks cover CSV rendering only.

At the user's request, `python verify.py` was rerun on 2026-10-03 after acceptance of the CSV behavior; it again exited 0 with the same passing result. Neither exporter nor checker was edited. This rerun checks the catalog, mixed-case/quoted-name and empty-input cases, including expected magnitudes and unchanged input. It does not rerun the additional assertions above, exercise the printer template, confirm the reported clipping or establish delivery acceptance.

To recheck from the repository root, run `python verify.py`. To reproduce the CSV locally:

```sh
python -B -c 'import json; from pathlib import Path; from exporter import render_catalog; rows=json.loads(Path("catalog.json").read_text()); Path("docs/observing-cards.csv").open("w",newline="").write(render_catalog(rows))'
```

## Later volunteer session

Use the prepared CSV in the volunteer's normal card workflow. Confirm it imports as two columns and retains every expected name and magnitude. For the print trial, report the CSV used, trial date, layout/settings that affect alignment, whether names and magnitudes remain paired and readable, and any clipping, wrapping, offsets or unexpected page breaks. Identify affected cards and describe the observed result concretely. No print settings or measurements have yet been supplied; do not assume them.

Return observations in a later message. This agent must work only in this synthetic repository and must not contact a printer or any external system.

## Print reports and remaining owner inspection

The [latest report](.project-efforts/observing-card-delivery/evidence/E2-volunteer-print-recheck.md), relayed by the user on 2026-10-03, says three of three cards printed and Sirius's minus sign is visible. This is a secondhand volunteer report; it supplies no alignment assessment, complete printed magnitude transcription or specific template adjustment. The user still needs to inspect alignment before accepting the batch.

The [earlier failed-trial report](.project-efforts/observing-card-delivery/evidence/E1-volunteer-print-report.md) preserves the initially missing minus sign and the volunteer's template-clipping explanation. The two-card claim was corrected to three. The latest result supersedes the outstanding sign concern at the report level; it does not independently verify the cause. No new clipping investigation or repeat trial is required unless owner inspection finds a defect.

Next, the owner inspects alignment and readability of all three printed cards, checks complete names and magnitudes against the table above, and confirms correct name/value pairing with no clipping or overlap. Record the inspection outcome and explicit batch acceptance or required corrections. No code changes or external contact are authorized for this agent. Final acceptance remains pending that inspection and decision.

## Project owner review and acceptance

The user accepted keeping the current CSV format and sorting on 2026-10-03 and stated that the volunteer would adjust the printer template. No code changes are authorized for this step. [D1](.project-efforts/observing-card-delivery/decisions.md#d1--retain-the-current-csv-format-and-sorting) maintains this scoped choice. The reported recheck supports moving to owner inspection; it does not establish final acceptance.

Volunteer observations are saved with their source, scope and limitations. Owner alignment review can now proceed; record the owner's explicit conclusion and any required corrections. A volunteer report or passing local check does not establish owner acceptance. Final acceptance remains pending owner inspection and decision.

Resume prompt: “Continue observing-card delivery from .project-efforts/observing-card-delivery/map.md; record the volunteer print observations and prepare the project owner's alignment review.” Include the observations with that prompt.

Keep catalog.json, README.md and verify.py unchanged throughout this scope. Retain the effort map while required acceptance work remains.

## Short recheck checklist

- Use the current prepared CSV and record the template setting changed and trial date.
- Check preview and paper both show three cards, ordered Alpha, Test; Polaris; Sirius.
- Confirm each complete name and magnitude: Alpha, Test — `4.1`; Polaris — `2.0`; Sirius — `-1.46`, including its minus sign.
- Check alignment, readability and absence of clipping, wrapping or unexpected page breaks; report any remaining defects in text.
- Supply the observations for the project owner's alignment review and record their conclusion before final acceptance.
