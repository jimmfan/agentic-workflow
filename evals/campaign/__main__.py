"""Command-line entry point; live execution always needs an explicit flag."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from evals.campaign import calibration, core
from evals.campaign.schema import load_spec, read_json


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="action", required=True)
    validate = commands.add_parser(
        "validate", help="Validate scenarios and budget without model use"
    )
    validate.add_argument("spec", type=Path)
    freeze = commands.add_parser(
        "freeze", help="Freeze immutable product payloads and experiment inputs"
    )
    freeze.add_argument("spec", type=Path)
    freeze.add_argument("--out", type=Path, required=True)
    freeze.add_argument("--repo", type=Path, default=core.ROOT)
    for name in ("calibration-packet", "calibration-assess"):
        command = commands.add_parser(name)
        command.add_argument("source", type=Path)
        command.add_argument("--out", type=Path)
        if name == "calibration-assess":
            command.add_argument("--review", required=True, type=Path)
    for name in (
        "status",
        "packet",
        "report",
        "begin",
        "record",
        "grade",
        "run",
        "recover",
    ):
        command = commands.add_parser(name)
        command.add_argument("campaign", type=Path)
        if name in {"begin", "record", "recover"}:
            command.add_argument("--run", required=True)
        if name == "record":
            command.add_argument("--response", required=True, type=Path)
        if name == "grade":
            command.add_argument("--review", required=True, type=Path)
        if name == "recover":
            command.add_argument("--reason", required=True)
        if name in {"packet", "report"}:
            command.add_argument("--out", type=Path)
        if name == "run":
            command.add_argument("--allow-live", action="store_true")
            command.add_argument("--run")
    return result


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.action == "calibration-packet":
            packet = calibration.make_packet(args.source)
            value = {"packet_sha256": core.fingerprint(packet), "packet": packet}
        elif args.action == "calibration-assess":
            value = calibration.assess(args.source, read_json(args.review))
        elif args.action == "validate":
            spec, scenarios = load_spec(args.spec)
            value = {
                "valid": True,
                "name": spec["name"],
                "scenarios": [
                    {
                        "id": s["id"],
                        "turns": len(s["turns"]),
                        "checks": sum(len(t["checks"]) for t in s["turns"]),
                        "applicability": s["applicability"],
                    }
                    for s, _ in scenarios
                ],
                "conditions": [c["id"] for c in spec["conditions"]],
            }
        elif args.action == "freeze":
            manifest = core.freeze_campaign(args.spec, args.out, repo=args.repo)
            value = {
                "campaign": str(args.out.resolve()),
                "manifest_sha256": core.fingerprint(manifest),
                "expected_turns": manifest["expected_turns"],
                "schedule": manifest["schedule"],
            }
        elif args.action == "status":
            core.verify_campaign(args.campaign)
            value = read_json(args.campaign / "state.json")
        elif args.action == "begin":
            value = core.begin_turn(args.campaign, args.run)
        elif args.action == "record":
            value = core.finish_turn(args.campaign, args.run, read_json(args.response))
        elif args.action == "recover":
            value = core.recover_turn(args.campaign, args.run, args.reason)
        elif args.action == "packet":
            packet = core.grading_packet(args.campaign)
            value = {"packet_sha256": core.fingerprint(packet), "packet": packet}
        elif args.action == "grade":
            value = core.apply_review(args.campaign, read_json(args.review))
        elif args.action == "run":
            value = core.run_campaign(
                args.campaign, allow_live=args.allow_live, run_id=args.run
            )
        else:
            value = core.report_campaign(args.campaign)
        if getattr(args, "out", None) is not None and args.action in {
            "packet",
            "report",
            "calibration-packet",
            "calibration-assess",
        }:
            outputs = [args.out]
            if args.action == "report":
                if args.out.suffix != ".json":
                    raise ValueError(
                        "Report --out must end in .json; Markdown is written beside it"
                    )
                outputs.append(args.out.with_suffix(".md"))
            if any(path.exists() or path.is_symlink() for path in outputs):
                raise ValueError(
                    "Output already exists; choose a new evidence/report file"
                )
            core.dump(args.out, value)
            if args.action == "report":
                args.out.with_suffix(".md").write_text(
                    core.render_report(value), encoding="utf-8"
                )
        else:
            print(json.dumps(value, indent=2, ensure_ascii=False))
        if args.action in {"report", "run", "grade", "calibration-assess"}:
            return {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}[value["verdict"]]
        return 0
    except (ValueError, RuntimeError, OSError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
