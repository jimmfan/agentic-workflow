# Boolean configuration fixture

`parse_bool` accepts `true`, `yes`, and `1` as true; `false`, `no`, and `0` as
false. Matching is case-insensitive after trimming whitespace. Other values
raise `ValueError`.

Validate with `python verify.py`.

