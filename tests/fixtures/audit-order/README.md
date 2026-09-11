# Order summaries

`uv run --no-project python -m unittest -v` runs tests without dependencies.
`summarize` is the public integration seam: read JSON lines from an input file and return an account-to-total mapping.
Empty input returns an empty mapping; account totals aggregate integer cents.
The existing behavior is accepted.
