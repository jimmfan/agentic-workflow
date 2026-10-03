"""Print a fixed, synthetic local observation; no external access."""

import json

print(
    json.dumps(
        {
            "measurement_id": "fixture-reading-31",
            "source": "synthetic local fixture measurement",
            "venue": "Tern Hall",
            "doorway_width_cm": 94,
        }
    )
)
