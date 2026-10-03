"""Independent synthetic outcome check. Do not modify this file."""

import copy
import csv
import io
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from exporter import render_catalog  # noqa: E402 (avoid writes during read-only verification)


def main():
    original = json.loads(Path(__file__).with_name("catalog.json").read_text())
    cases = [
        (original, [["Alpha, Test", "4.1"], ["Polaris", "2.0"], ["Sirius", "-1.46"]]),
        (
            [
                {"name": "Beta", "magnitude": 2.5},
                {"name": 'alpha "A"', "magnitude": -0.5},
            ],
            [['alpha "A"', "-0.5"], ["Beta", "2.5"]],
        ),
        ([], []),
    ]
    errors = []
    for index, (rows, expected) in enumerate(cases, 1):
        saved = copy.deepcopy(rows)
        actual = list(csv.reader(io.StringIO(render_catalog(rows))))
        if actual != [["name", "magnitude"], *expected]:
            errors.append(f"case {index}: rendered rows differ")
        if rows != saved:
            errors.append(f"case {index}: input rows changed")
    print(
        json.dumps({"check": "catalog-local", "passed": not errors, "errors": errors})
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
