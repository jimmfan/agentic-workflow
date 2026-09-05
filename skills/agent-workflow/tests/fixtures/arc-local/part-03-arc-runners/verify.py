from pathlib import Path
import re


def main() -> int:
    root = Path(__file__).resolve().parent
    values = (root / "values.yaml").read_text()
    readme = (root / "README.md").read_text()
    match = re.search(r"^runnerScaleSetName: ([a-z0-9-]+)$", values, re.MULTILINE)
    passed = bool(match) and all(
        f"{key}: {match[1]}" in readme for key in ("runnerScaleSetName", "runs-on")
    )
    print("PASS: local ARC references" if passed else "FAIL: local ARC references")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
