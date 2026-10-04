# Observing-card CSV handoff

## Status

Local implementation and preparation are complete. The latest volunteer report
says three of three cards printed and Sirius's minus sign is now visible.
The repeat-trial result is reported, not independently inspected here. The
project owner still needs to inspect printed alignment before accepting the
batch. The user accepts keeping the current CSV format and sorting behavior;
final printed-delivery acceptance remains pending. No code changes are
authorized for this step. No image is available here.
All work stayed in this synthetic repository; no printer or external system was
contacted.

## Implementation and checks

`exporter.py` uses Python's CSV writer to escape commas, quotes, and line breaks.
Rows sort by the name's Unicode `casefold()` value; equal keys retain supplied
order. Magnitudes are passed directly to the writer without rounding or
normalization; supplied strings retain their formatting. Numeric values use
Python's string representation. Sorting creates a new list and does not modify
the supplied list or its records. Output includes the `name,magnitude` header
and standard CSV CRLF record endings.

`catalog.json`, `README.md`, and `verify.py` were left unchanged.

Checks run successfully:

- `python verify.py` reported `passed: true`, with no errors.
- `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`
  passed both added tests, including embedded CR/LF, Unicode case folding,
  stable ordering, magnitude formatting, and input preservation.

## Volunteer session

The prepared trial input is `docs/observing-card.csv`, rendered from the existing
synthetic catalog. Use it in the usual card layout workflow. This CSV is data,
not a finished card layout; local checks do not establish printed alignment.
The volunteer performs the print trial and sends observations in a later
message. This agent must not contact a printer or an external system.

Before using a later checkout, rerun the checks above. If the exporter changes,
regenerate the trial input from the repository root with:

```sh
PYTHONDONTWRITEBYTECODE=1 python -c 'import json; from pathlib import Path; from exporter import render_catalog; rows = json.loads(Path("catalog.json").read_text()); output = Path("docs/observing-card.csv").open("w", encoding="utf-8", newline=""); output.write(render_catalog(rows)); output.close()'
```

Record the following with the trial observations:

- Trial date and input revision or exact CSV used.
- Layout application, paper/card size, orientation, scale, and margin settings.
- Whether names appear in the expected order, `Alpha, Test` stays in one field,
  and the supplied magnitudes appear correctly.
- Any clipping, wrapping, column displacement, or misalignment against the card
  boundaries; include measurements and affected rows where possible.
- Proposed corrections and whether another trial is needed.

## Owner review and final acceptance

After the volunteer's observations arrive, record them here and address any
reported issues within the authorized repository scope. Rerun local checks for
code changes and request another volunteer trial if printed results need
confirmation. The project owner then reviews the printed alignment and records
acceptance or requested corrections, identifying the trial being reviewed.
Local verification alone does not complete delivery.

- CSV format and sorting behavior: accepted by the user on 2026-10-03.
- Volunteer observations: latest report says three of three cards printed and
  Sirius's minus sign is visible. Not independently inspected here.
- Follow-up corrections / repeat trial: reported card-count and missing-sign
  issues are resolved in the latest trial; no further trial is currently
  required unless the owner review finds an issue.
- Project owner alignment review: pending.
- Final acceptance: pending owner printed-alignment review and acceptance.

## Print-trial history

On 2026-10-03 the user initially relayed that only two cards printed. The
volunteer subsequently corrected this: all three printed. The missing-card
report is superseded and no missing-card investigation is needed on current
evidence. At that stage, Sirius's minus sign was still missing on the printed card. The user
reports that the CSV includes `-1.46` and the volunteer attributes the defect
to the printer template clipping that field. The user has not inspected the
printer; no image is available here. Treat clipping as a reported diagnosis,
not an independently confirmed cause. Exact template settings remain unknown.

Local follow-up confirms `docs/observing-card.csv` contains all three data rows
and the Sirius field is `-1.46`. `python verify.py` still reports `passed: true`
with no errors. This establishes the local data only, not what was imported,
rendered, or printed during the trial. No exporter change is justified yet.

The investigation checklist prepared before the latest repeat-trial report was:

1. Record the exact CSV and template used, layout application, and print settings.
2. Check the reported clipping in the template and layout preview. Inspect the
   magnitude field's bounds, position, padding, and alignment to determine what
   cuts off the minus sign.
3. Correct the template as indicated by that inspection so the full `-1.46`
   fits visibly within the card. Preserve the CSV magnitude; do not remove or
   alter the sign to accommodate the layout. No exporter change is warranted
   by the current evidence. The template is not available for editing here.
4. Repeat the trial and report all three cards, Sirius's visible minus sign,
   and alignment/clipping observations. The owner then reviews the printed
   output before accepting delivery.

No printer or external system was contacted for this follow-up. These are
historical instructions, not evidence that this agent performed printer checks.

The latest update on 2026-10-03 reports three of three cards printed and Sirius's
minus sign visible. This supersedes the missing-sign observation. The exact
template adjustment was not supplied; do not infer specific settings or an
independently verified cause. The owner explicitly still needs to inspect
alignment before accepting the batch. Review the latest printed trial for
field clipping and alignment, then record acceptance or specific corrections.

A later session should read this file and `docs/delivery.md`, incorporate the
incoming observations, and keep these status entries current. Do not infer a
successful trial or owner approval from the passing local checks.

## Short recheck checklist after the template adjustment

- Record the adjusted template/version, exact CSV used, and print settings.
- Confirm preview and printed output contain all three cards in order:
  `Alpha, Test`, `Polaris`, `Sirius`.
- Confirm the printed magnitudes are `4.1`, `2.0`, and `-1.46` respectively,
  with Sirius's minus sign fully visible.
- Check all fields for clipping and alignment within the card boundaries;
  record the repeat-trial observations here.
- Have the project owner review that printed trial and record acceptance or
  remaining corrections.

The card count and visible Sirius minus sign are now reported as passing. The
checklist above remains available for the owner's inspection; other printed
details have not been independently verified here. Final delivery is blocked
only on the owner's printed-alignment review and acceptance, unless that review
identifies further corrections. CSV behavior is accepted; no code or CSV change is planned or
authorized for this step. The template is outside the available repository,
and this agent must not contact a printer or external system. Only documentation
was changed in this step.
