# Slug verification fixture

`slugify` must trim surrounding whitespace, lowercase text, replace each run of
non-alphanumeric characters with one hyphen, and omit leading/trailing hyphens.

Run `python verify.py` before editing and again after the fix. Every run appends
its exit code to `.behavior-evidence/verification.jsonl`.

