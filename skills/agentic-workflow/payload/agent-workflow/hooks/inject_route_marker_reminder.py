import json


REMINDER = (
    "End every user-facing final response with exactly one truthful final "
    "'[route: router → <executed path or terminal outcome>]' line. "
    "Report only what actually executed; use 'direct' when no workflow or "
    "skill ran. Do not reroute or perform additional work merely to produce "
    "the marker."
)


def main():
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": REMINDER,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
