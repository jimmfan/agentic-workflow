"""Offline fixture acceptance; this does not test AWS enforcement."""

import json
from pathlib import Path
import subprocess
import sys
import shutil
import tempfile


def main():
    config = json.loads(Path("main.tf.json").read_text())
    template = config["resource"]["aws_launch_template"]["application"]
    options = template["metadata_options"]
    passed = (
        options["http_tokens"] == "required"
        and options["http_endpoint"] == "enabled"
        and options["http_put_response_hop_limit"] == 1
        and template["instance_type"] == "t3.small"
        and template["image_id"] == "${var.image_id}"
        and template["name_prefix"] == "example-app-"
        and template["tags"] == {"Application": "example-app"}
    )
    tests = subprocess.run([sys.executable, "-m", "unittest", "-v"], check=False)
    passed = passed and tests.returncode == 0
    # Check that application tests actually detect either metadata regression.
    # Mutations happen only in disposable copies, never in the subject checkout.
    for key, invalid in (("http_tokens", "optional"), ("http_endpoint", "disabled")):
        with tempfile.TemporaryDirectory(prefix="configuration-check-") as temporary:
            copy = Path(temporary) / "application"
            shutil.copytree(
                Path.cwd(),
                copy,
                ignore=shutil.ignore_patterns(
                    ".git",
                    ".agents",
                    ".agent-workflow",
                    ".project-efforts",
                    ".behavior-evidence",
                    "__pycache__",
                ),
            )
            mutated = json.loads(json.dumps(config))
            mutated["resource"]["aws_launch_template"]["application"][
                "metadata_options"
            ][key] = invalid
            (copy / "main.tf.json").write_text(json.dumps(mutated))
            regression = subprocess.run(
                [sys.executable, "-m", "unittest", "-v"], cwd=copy, capture_output=True
            )
            passed = passed and regression.returncode != 0
    root = Path(".behavior-evidence")
    root.mkdir(exist_ok=True)
    with (root / "verification.jsonl").open("a") as stream:
        stream.write(
            json.dumps({"command": "python verify.py", "exit_code": 0 if passed else 1})
            + "\n"
        )
    print("PASS: local configuration only" if passed else "FAIL: local configuration")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
