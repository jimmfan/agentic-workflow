"""Render the fictional observing-card input as CSV."""


def render_catalog(rows):
    return "name,magnitude\n" + "".join(
        f"{row['name']},{row['magnitude']}\n" for row in rows
    )
