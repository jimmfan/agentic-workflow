"""Render the fictional observing-card input as CSV."""

import csv
import io


def render_catalog(rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["name", "magnitude"])
    for row in sorted(rows, key=lambda row: row["name"].casefold()):
        writer.writerow([row["name"], row["magnitude"]])
    return output.getvalue()
