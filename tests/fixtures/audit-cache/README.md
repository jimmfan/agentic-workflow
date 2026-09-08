# Account totals service

`uv run --no-project python -m unittest -v` runs the existing local suite without dependencies.
Reports must isolate accounts, reuse cached totals inside the configured TTL, and refresh at the TTL boundary.
Since the cache optimization, requesting alpha then beta at time 0 reports alpha=12 and beta=12, although the store holds beta=31.
Calling beta on a fresh service returns 31.
No fix has been diagnosed.
