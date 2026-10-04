"""Render the fictional observing-card input as CSV."""

import csv
import io


def render_catalog(rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(("name", "magnitude"))
    writer.writerows(
        (row["name"], row["magnitude"])
        for row in sorted(rows, key=lambda row: row["name"].casefold())
    )
    return output.getvalue()
