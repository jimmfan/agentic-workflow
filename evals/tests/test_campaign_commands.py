"""Command observation controls use retained events, not real model runs."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from evals.campaign import core
from evals.campaign.revisions import snapshot_files


class CommandObservationControls(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="campaign-command-controls-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        fixture = self.root / "fixture"
        fixture.mkdir()
        (fixture / "verify.py").write_text("print('verification result')\n")
        self.campaign = self.root / "campaign"

    def observe(self, records, *, target="verify.py"):
        turns = [
            {
                "id": f"T{index}",
                "session": "subject",
                "request": "Run python verify.py and report its result.",
                "allowed_writes": [],
                "checks": [
                    {
                        "id": "verifier-invoked",
                        "kind": "command_observed",
                        "argv_contains": target,
                    }
                ],
            }
            for index in range(1, len(records) + 1)
        ]
        core.dump(
            self.root / "scenario.json",
            {
                "schema": 1,
                "id": "command-controls",
                "title": "Command execution evidence",
                "question": "Was the named verifier invoked?",
                "fixture": "fixture",
                "applicability": "common-outcome",
                "turns": turns,
            },
        )
        core.dump(
            self.root / "spec.json",
            {
                "schema": 1,
                "name": "commands",
                "question": "Was the named verifier invoked?",
                "scenarios": ["scenario.json"],
                "conditions": [{"id": "candidate", "ref": "main"}],
                "repetitions": 1,
                "seed": 2,
                "limits": {
                    "max_turns": len(turns),
                    "turn_seconds": 5,
                    "campaign_seconds": 120,
                },
                "host": {
                    "kind": "manual",
                    "model": "unavailable",
                    "reasoning_effort": "unavailable",
                },
            },
        )

        def prepare(repo, ref, destination, **kwargs):
            destination.mkdir()
            (destination / "AGENTS.md").write_text("Synthetic framework\n")
            return {
                "ref": ref,
                "commit": "a" * 40,
                "version": "0.0.0",
                "layout": "test",
                "files": snapshot_files(destination),
                "warnings": [],
                "overlays": [],
            }

        with patch.object(core, "prepare_revision", side_effect=prepare):
            core.freeze_campaign(self.root / "spec.json", self.campaign)
        results = []
        for index, record in enumerate(records, 1):
            request = core.begin_turn(self.campaign, "run-0001")
            trace = Path(request["artifact_dir"]) / "codex.jsonl"
            events = [
                {"type": "thread.started", "thread_id": "subject-one"},
                {
                    "type": "item.completed",
                    "item": {
                        "id": f"command-{index}",
                        "type": "command_execution",
                        "status": "completed",
                        "exit_code": 0,
                        **record,
                    },
                },
            ]
            trace.write_text("\n".join(json.dumps(event) for event in events))
            checkpoint = core.finish_turn(
                self.campaign,
                "run-0001",
                {
                    "schema": 1,
                    "execution_status": "completed",
                    "session_id": "subject-one",
                    "response": "Synthetic subject claim; not execution evidence.",
                    "traces": [str(trace)],
                },
            )
            results.append(
                next(
                    check["verdict"]
                    for check in checkpoint["checks"]
                    if check["id"] == "verifier-invoked"
                )
            )
        return results

    def test_filename_mentions_do_not_establish_execution(self):
        commands = [
            "cat verify.py",
            "echo verify.py",
            "echo python verify.py",
            "printf '%s' 'python verify.py'",
            "python another.py verify.py",
            "python verify.py.backup",
            "python unrelated/verify.py",
            "python verify.py/",
            "python -c 'pass' verify.py",
            "python -m another verify.py",
            "python --help verify.py",
            "python -V verify.py",
            "/bin/bash -lc 'cat verify.py'",
        ]
        verdicts = self.observe([{"command": command} for command in commands])
        for command, verdict in zip(commands, verdicts):
            with self.subTest(command=command):
                self.assertEqual(verdict, "INCONCLUSIVE")

    def test_literal_script_execution_is_observed_in_supported_launch_forms(self):
        commands = [
            "python verify.py",
            "python3 ./verify.py",
            "/usr/bin/python3.13 -B -u verify.py",
            "python -I -- 'verify.py' --report",
            "./verify.py",
            "/bin/bash -lc 'python verify.py'",
            '/bin/sh -c "python3 ./verify.py"',
        ]
        verdicts = self.observe([{"command": command} for command in commands])
        for command, verdict in zip(commands, verdicts):
            with self.subTest(command=command):
                self.assertEqual(verdict, "PASS")

    def test_shell_control_flow_or_expansion_does_not_prove_invocation(self):
        commands = [
            "false && python verify.py",
            "true || python verify.py",
            "echo verify.py; true",
            "python verify.py | cat",
            "python verify.py > result.txt",
            "# python verify.py",
            "echo harmless\npython verify.py",
            "python ${SCRIPT:-verify.py}",
            "python verify.py$(echo .backup)",
            "python verify.py`echo .backup`",
            "python 'verify.py",
            "/bin/bash -lc 'false && python verify.py'",
            "env SCRIPT=verify.py echo done",
        ]
        verdicts = self.observe([{"command": command} for command in commands])
        for command, verdict in zip(commands, verdicts):
            with self.subTest(command=command):
                self.assertEqual(verdict, "INCONCLUSIVE")

    def test_leading_current_directory_prefix_is_equivalent_in_both_positions(self):
        commands = [
            "python verify.py",
            "python ./verify.py",
            "python ././verify.py",
            "./verify.py",
            "python ./verify.py/",
            "python alias/../verify.py",
        ]
        self.assertEqual(
            self.observe(
                [{"command": command} for command in commands], target="./verify.py"
            ),
            ["PASS", "PASS", "PASS", "PASS", "INCONCLUSIVE", "INCONCLUSIVE"],
        )
        aliases = [
            ("python .//verify.py", "/verify.py"),
            ("python /verify.py", ".//verify.py"),
            ("python ././/verify.py", "/verify.py"),
            ("python /verify.py", "././/verify.py"),
        ]
        for index, (command, target) in enumerate(aliases):
            with self.subTest(command=command, target=target):
                self.campaign = self.root / f"alias-campaign-{index}"
                self.assertEqual(
                    self.observe([{"command": command}], target=target),
                    ["INCONCLUSIVE"],
                )

    def test_invocation_requires_completion_and_exit_code_but_not_success(self):
        records = [
            {"command": "python verify.py", "exit_code": 1},
            {"command": "python verify.py", "exit_code": None},
            {"command": "python verify.py", "status": "in_progress"},
            {"command": "python verify.py", "status": "failed"},
            {"command": None},
        ]
        self.assertEqual(
            self.observe(records),
            ["PASS", "INCONCLUSIVE", "INCONCLUSIVE", "INCONCLUSIVE", "INCONCLUSIVE"],
        )


if __name__ == "__main__":
    unittest.main()
