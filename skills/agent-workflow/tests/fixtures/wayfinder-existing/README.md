# Existing Wayfinder fixture

The canonical project-owned map is
`.agent-wayfinder/response-serialization/map.md`. Implement only its
actionable `Next work` slice, consume the settled D1 decision, leave the unrelated
non-blocking U1 child unloaded and unchanged, and validate with
`python verify.py`.

The project owner accepted compact, lexicographically sorted JSON for public
responses. The exact current decision is the D1 section in `decisions.md`; the
map links directly to that section so a fresh session can retrieve it without
loading the unrelated U1 detail.
