# Existing Wayfinder fixture

The canonical project-owned map is
`.agent-wayfinder/response-serialization/map.md`. Implement only its
actionable `Next work` slice, consume the settled D1 decision, leave the unrelated
non-blocking U1 child unloaded and unchanged, and validate with
`python verify.py`.
