from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PACKAGE = Path(__file__).resolve().parent.parent
CONTROLLER_PATH = PACKAGE / "payload/ai-workflow/runtime/controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("agentic_workflow_controller", CONTROLLER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load controller")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


CONTROLLER = load_controller()


class ControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="agentic-workflow-controller-test-")
        self.root = Path(self.temporary.name).resolve()
        declaration = {
            "configuration": {
                "issue-tracker": {
                    "path": "docs/agents/issue-tracker.md",
                    "provisioned_by": "setup",
                }
            },
            "hosts": {
                "github-copilot": {
                    "availability": "available",
                    "explicit_prefix": "/",
                },
                "codex": {"availability": "available", "explicit_prefix": "$"},
                "claude-code": {"availability": "unavailable", "explicit_prefix": "/"},
            },
            "provider": {
                "skills": [
                    {
                        "name": "wayfinder",
                        "invocation": {
                            "github-copilot": "user-only",
                            "codex": "user-only",
                            "claude-code": "unavailable",
                        },
                        "requires_configuration": [],
                    },
                    {
                        "name": "research",
                        "invocation": {
                            "github-copilot": "implicit",
                            "codex": "implicit",
                            "claude-code": "unavailable",
                        },
                        "requires_configuration": [],
                    },
                ]
            },
        }
        providers = self.root / ".ai-workflow/providers.json"
        providers.parent.mkdir(parents=True)
        providers.write_text(json.dumps(declaration), encoding="utf-8")
        active = self.root / ".ai-workflow-state/active.md"
        active.parent.mkdir(parents=True)
        active.write_text("# Active workflow\n\n- Active workflow: none\n", encoding="utf-8")
        for name in ("wayfinder", "research"):
            skill = self.root / ".agents/skills" / name / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(f"# {name}\n", encoding="utf-8")
        self.payload = {
            "cwd": str(self.root),
            "session_id": "test-session",
            "timestamp": "2026-08-14T00:00:00Z",
        }
        self.state = CONTROLLER.new_state(self.root, self.payload, "vscode")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_controller_requires_supported_python(self) -> None:
        self.assertEqual(CONTROLLER.MINIMUM_PYTHON, (3, 11))
        with mock.patch.object(CONTROLLER.sys, "version_info", (3, 10, 14)):
            with self.assertRaisesRegex(CONTROLLER.ControllerError, "Python 3.11 or newer"):
                CONTROLLER.require_supported_python()

    def test_project_root_resolves_installation_from_nested_working_directory(self) -> None:
        nested = self.root / "packages/service/src"
        nested.mkdir(parents=True)
        self.assertEqual(
            CONTROLLER.project_root({**self.payload, "cwd": str(nested)}),
            self.root,
        )

    def management(self, command: str) -> str:
        payload = {
            **self.payload,
            "tool_name": "run_in_terminal",
            "tool_input": {"command": command},
            "tool_use_id": command,
        }
        output, changed = CONTROLLER.handle_pre_tool(
            payload, self.state, self.root, "vscode"
        )
        self.assertTrue(changed)
        specific = output.get("hookSpecificOutput", {})
        self.assertEqual(specific.get("permissionDecision"), "allow", output)
        return str(specific.get("additionalContext", ""))

    def test_session_bootstrap_is_actionable_before_the_first_tool(self) -> None:
        output = CONTROLLER.handle_hook(
            {**self.payload, "hook_event_name": "SessionStart", "source": "new"},
            "vscode",
        )
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("For every user prompt", context)
        self.assertIn("`direct` is valid", context)
        self.assertIn("controller.py checkpoint --route direct", context)
        self.assertIn("--next-action read-only", context)
        self.assertIn("controller.py action --kind <kind>", context)
        self.assertIn("never expand user authority", context)
        CONTROLLER.remove_state(CONTROLLER.state_path(self.root, self.payload, "vscode"))

    def test_route_checkpoint_is_required_before_substantive_tool(self) -> None:
        output, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "run_in_terminal",
                "tool_input": {"command": "git status"},
                "tool_use_id": "one",
            },
            self.state,
            self.root,
            "vscode",
        )
        specific = output["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        reason = specific["permissionDecisionReason"]
        self.assertIn("Route checkpoint missing", reason)
        self.assertIn("controller.py checkpoint", reason)
        self.assertIn("`direct` is valid", reason)
        self.assertIn("--next-action <kind>", reason)
        self.assertIn("never grant authority", reason)

        output, _changed = CONTROLLER.handle_pre_tool(
            {**self.payload, "tool_name": "read_file", "tool_input": {"path": "README.md"}},
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(output, {})

        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint --route direct "
            "--repository-write allowed --verification not-required"
        )
        allowed, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "editFiles",
                "tool_input": {"files": ["docs/direct.md"]},
                "tool_use_id": "direct-write",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(allowed, {})

    def test_exact_declaration_is_auto_approved_but_shell_lookalikes_are_not(self) -> None:
        valid = {
            **self.payload,
            "tool_name": "run_in_terminal",
            "tool_input": {
                "command": (
                    "python3 .ai-workflow/runtime/controller.py checkpoint --route direct "
                    "--mode read-only --repository-write denied --verification not-required"
                )
            },
            "tool_use_id": "valid-declaration",
        }
        accepted, changed = CONTROLLER.handle_pre_tool(
            valid, self.state, self.root, "vscode"
        )
        self.assertTrue(changed)
        self.assertEqual(
            accepted["hookSpecificOutput"]["permissionDecision"],
            "allow",
        )

        for command in (
            "python3 .ai-workflow/runtime/controller.py checkpoint --route direct; touch x",
            "python3 .ai-workflow/runtime/controller.py checkpoint --route $(touch x)",
            "/usr/bin/python3 .ai-workflow/runtime/controller.py checkpoint --route direct",
            "python3 /tmp/.ai-workflow/runtime/controller.py checkpoint --route direct",
        ):
            fresh = CONTROLLER.new_state(self.root, self.payload, "vscode")
            denied, changed = CONTROLLER.handle_pre_tool(
                {
                    **self.payload,
                    "tool_name": "run_in_terminal",
                    "tool_input": {"command": command},
                    "tool_use_id": command,
                },
                fresh,
                self.root,
                "vscode",
            )
            self.assertFalse(changed, command)
            self.assertEqual(
                denied["hookSpecificOutput"]["permissionDecision"],
                "deny",
                command,
            )
            self.assertIsNone(fresh["route"], command)

        fresh = CONTROLLER.new_state(self.root, self.payload, "vscode")
        ambiguous_fields, changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "run_in_terminal",
                "tool_input": {
                    "command": valid["tool_input"]["command"],
                    "script": "touch x",
                },
                "tool_use_id": "ambiguous-command-fields",
            },
            fresh,
            self.root,
            "vscode",
        )
        self.assertFalse(changed)
        self.assertEqual(
            ambiguous_fields["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertIsNone(fresh["route"])

        fresh = CONTROLLER.new_state(self.root, self.payload, "vscode")
        read_output, changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "read_file",
                "tool_input": {
                    "command": (
                        "python3 .ai-workflow/runtime/controller.py checkpoint --route direct"
                    )
                },
                "tool_use_id": "wrong-tool",
            },
            fresh,
            self.root,
            "vscode",
        )
        self.assertTrue(changed)
        self.assertEqual(read_output, {})
        self.assertIsNone(fresh["route"])

    def test_diagnosis_checkpoint_denies_native_repository_write(self) -> None:
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint "
            "--route debugging --mode diagnosis --verification not-required"
        )
        output, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "editFiles",
                "tool_input": {"files": ["src/app.py"]},
                "tool_use_id": "write",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("diagnosis", output["hookSpecificOutput"]["permissionDecisionReason"])

        read, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "read_file",
                "tool_input": {"path": "src/app.py"},
                "tool_use_id": "read",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(read, {})

        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint --route implement "
            "--mode normal --repository-write allowed --verification required"
        )
        allowed, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "editFiles",
                "tool_input": {"files": ["src/app.py"]},
                "tool_use_id": "authorized-write",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(allowed, {})

    def test_opaque_action_needs_explicit_single_use_classification(self) -> None:
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint "
            "--route direct --mode read-only --verification not-required"
        )
        shell = {
            **self.payload,
            "tool_name": "run_in_terminal",
            "tool_input": {"command": "git status"},
            "tool_use_id": "shell",
        }
        denied, _changed = CONTROLLER.handle_pre_tool(shell, self.state, self.root, "vscode")
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")
        self.management(
            "python3 .ai-workflow/runtime/controller.py action --kind read-only"
        )
        allowed, _changed = CONTROLLER.handle_pre_tool(shell, self.state, self.root, "vscode")
        self.assertEqual(allowed, {})
        denied_again, _changed = CONTROLLER.handle_pre_tool(
            {**shell, "tool_use_id": "shell-two"}, self.state, self.root, "vscode"
        )
        self.assertEqual(denied_again["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_terminal_commands_stay_opaque_and_use_declared_authority(self) -> None:
        context = self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint --route direct "
            "--mode read-only --repository-write denied --verification not-required "
            "--next-action read-only"
        )
        self.assertIn("route checkpoint recorded", context)

        read = {
            **self.payload,
            "tool_name": "run_in_terminal",
            "tool_input": {"command": "git log -3 --oneline"},
            "tool_use_id": "read-git-history",
        }
        allowed, _changed = CONTROLLER.handle_pre_tool(
            read, self.state, self.root, "vscode"
        )
        self.assertEqual(allowed, {})
        CONTROLLER.handle_post_tool(read, self.state)
        self.assertFalse(self.state["repository_changed"])
        self.assertEqual(self.state["last_successful_tool"]["kind"], "read-only")

        ambiguous, _changed = CONTROLLER.handle_pre_tool(
            {
                **read,
                "tool_input": {"command": "python3 scripts/report.py"},
                "tool_use_id": "ambiguous-command",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(
            ambiguous["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertIn(
            "Declare the next opaque tool action",
            ambiguous["hookSpecificOutput"]["permissionDecisionReason"],
        )

        self.management(
            "python3 .ai-workflow/runtime/controller.py action --kind repository-write"
        )
        mutating, _changed = CONTROLLER.handle_pre_tool(
            {
                **read,
                "tool_input": {"command": "touch generated.txt"},
                "tool_use_id": "mutating-command",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(
            mutating["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertIn(
            "read-only route checkpoint",
            mutating["hookSpecificOutput"]["permissionDecisionReason"],
        )

    def test_external_and_destructive_declarations_remain_authorization_gated(self) -> None:
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint "
            "--route direct --verification not-required"
        )
        self.management(
            "python3 .ai-workflow/runtime/controller.py action --kind external-mutation"
        )
        payload = {
            **self.payload,
            "tool_name": "mcp__tracker__create_issue",
            "tool_input": {"title": "test"},
            "tool_use_id": "external",
        }
        denied, _changed = CONTROLLER.handle_pre_tool(payload, self.state, self.root, "vscode")
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("external mutation", denied["hookSpecificOutput"]["permissionDecisionReason"])

        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint --route direct "
            "--external-mutation allowed --destructive allowed --verification not-required"
        )
        self.management(
            "python3 .ai-workflow/runtime/controller.py action --kind external-mutation"
        )
        allowed, _changed = CONTROLLER.handle_pre_tool(payload, self.state, self.root, "vscode")
        self.assertEqual(allowed, {})

    def test_user_only_provider_cannot_claim_execution_without_prompt_invocation(self) -> None:
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint "
            "--route wayfinder-handoff --verification not-required --provider wayfinder"
        )
        with self.assertRaisesRegex(CONTROLLER.ControllerError, "user-only"):
            CONTROLLER.apply_management(
                CONTROLLER.command_parser().parse_args(
                    ["provider", "--name", "wayfinder", "--outcome", "started"]
                ),
                self.state,
                self.root,
                "vscode",
            )
        self.state["user_invoked_providers"] = ["wayfinder"]
        started = CONTROLLER.apply_management(
            CONTROLLER.command_parser().parse_args(
                ["provider", "--name", "wayfinder", "--outcome", "started"]
            ),
            self.state,
            self.root,
            "vscode",
        )
        self.assertIn("started", started)
        message = CONTROLLER.apply_management(
            CONTROLLER.command_parser().parse_args(
                ["provider", "--name", "wayfinder", "--outcome", "executed"]
            ),
            self.state,
            self.root,
            "vscode",
        )
        self.assertIn("executed", message)

    def test_provider_execution_requires_declared_configuration(self) -> None:
        declaration_path = self.root / ".ai-workflow/providers.json"
        declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
        declaration["provider"]["skills"][1]["requires_configuration"] = ["issue-tracker"]
        declaration_path.write_text(json.dumps(declaration), encoding="utf-8")
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint "
            "--route research --repository-write allowed --verification not-required"
        )
        self.assertEqual(self.state["selected_providers"], ["research"])
        denied, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "editFiles",
                "tool_input": {"files": ["src/app.py"]},
                "tool_use_id": "provider-before-start",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertIn(
            "validated started",
            denied["hookSpecificOutput"]["permissionDecisionReason"],
        )
        read_denied, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "read_file",
                "tool_input": {"path": "README.md"},
                "tool_use_id": "provider-read-before-start",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertIn(
            "validated started",
            read_denied["hookSpecificOutput"]["permissionDecisionReason"],
        )
        provider = CONTROLLER.command_parser().parse_args(
            ["provider", "--name", "research", "--outcome", "started"]
        )
        with self.assertRaisesRegex(CONTROLLER.ControllerError, "before a validated started"):
            CONTROLLER.apply_management(
                CONTROLLER.command_parser().parse_args(
                    ["provider", "--name", "research", "--outcome", "executed"]
                ),
                self.state,
                self.root,
                "vscode",
            )
        with self.assertRaisesRegex(CONTROLLER.ControllerError, "missing required configuration"):
            CONTROLLER.apply_management(provider, self.state, self.root, "vscode")

        configured = self.root / "docs/agents/issue-tracker.md"
        configured.parent.mkdir(parents=True)
        configured.write_text("Tracker: local\n", encoding="utf-8")
        started = CONTROLLER.apply_management(provider, self.state, self.root, "vscode")
        self.assertIn("started", started)
        message = CONTROLLER.apply_management(
            CONTROLLER.command_parser().parse_args(
                ["provider", "--name", "research", "--outcome", "executed"]
            ),
            self.state,
            self.root,
            "vscode",
        )
        self.assertIn("executed", message)

    def test_durable_state_conflict_requires_explicit_resolution_and_fresh_digest(self) -> None:
        active = self.root / ".ai-workflow-state/active.md"
        active.write_text("# Active workflow\n\n- Active workflow: implementation\n", encoding="utf-8")
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint --route discovery "
            "--repository-write allowed --verification required"
        )
        with self.assertRaisesRegex(CONTROLLER.ControllerError, "conflict"):
            CONTROLLER.apply_management(
                CONTROLLER.command_parser().parse_args(
                    ["durable", "--target", "discovery", "--resolution", "same"]
                ),
                self.state,
                self.root,
                "vscode",
            )
        self.management(
            "python3 .ai-workflow/runtime/controller.py durable "
            "--target discovery --resolution interrupt"
        )
        active.write_text(
            "# Active workflow\n\n- Active workflow: implementation\n- Notes: concurrent change\n",
            encoding="utf-8",
        )
        output, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "editFiles",
                "tool_input": {"files": [".ai-workflow-state/active.md"]},
                "tool_use_id": "durable-write",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("changed after validation", output["hookSpecificOutput"]["permissionDecisionReason"])

    def test_required_verification_needs_observed_satisfying_evidence(self) -> None:
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint --route implement "
            "--repository-write allowed --verification required"
        )
        write = {
            **self.payload,
            "tool_name": "editFiles",
            "tool_input": {"files": ["src/app.py"]},
            "tool_use_id": "write",
        }
        output, _changed = CONTROLLER.handle_pre_tool(write, self.state, self.root, "vscode")
        self.assertEqual(output, {})
        CONTROLLER.handle_post_tool(write, self.state)
        self.assertIn("required verification", "; ".join(CONTROLLER.stop_failures(self.state)))
        with self.assertRaisesRegex(CONTROLLER.ControllerError, "read/check action"):
            CONTROLLER.apply_management(
                CONTROLLER.command_parser().parse_args(
                    [
                        "evidence",
                        "--kind",
                        "tests",
                        "--result",
                        "passed",
                        "--satisfies",
                        "yes",
                    ]
                ),
                self.state,
                self.root,
                "vscode",
            )

        self.management(
            "python3 .ai-workflow/runtime/controller.py action --kind read-only"
        )
        check = {
            **self.payload,
            "tool_name": "run_in_terminal",
            "tool_input": {"command": "python3 -m unittest"},
            "tool_use_id": "check",
        }
        output, _changed = CONTROLLER.handle_pre_tool(check, self.state, self.root, "vscode")
        self.assertEqual(output, {})
        CONTROLLER.handle_post_tool(check, self.state)
        self.management(
            "python3 .ai-workflow/runtime/controller.py evidence "
            "--kind tests --result passed --satisfies yes"
        )
        self.assertEqual(CONTROLLER.stop_failures(self.state), [])

    def test_minor_direct_write_can_explicitly_skip_broad_verification(self) -> None:
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint --route direct "
            "--repository-write allowed --verification not-required"
        )
        write = {
            **self.payload,
            "tool_name": "editFiles",
            "tool_input": {"files": ["docs/note.md"]},
            "tool_use_id": "minor-write",
        }
        output, _changed = CONTROLLER.handle_pre_tool(write, self.state, self.root, "vscode")
        self.assertEqual(output, {})
        CONTROLLER.handle_post_tool(write, self.state)
        self.assertEqual(CONTROLLER.stop_failures(self.state), [])

    def test_durable_state_symlink_is_rejected(self) -> None:
        active = self.root / ".ai-workflow-state/active.md"
        outside = self.root / "outside-active.md"
        outside.write_text("# Active workflow\n\n- Active workflow: none\n", encoding="utf-8")
        active.unlink()
        active.symlink_to(outside)
        with self.assertRaisesRegex(CONTROLLER.ControllerError, "non-symlink"):
            CONTROLLER.parse_active_workflow(self.root)

    def test_missing_active_state_is_idle_and_allows_a_validated_first_write(self) -> None:
        active = self.root / ".ai-workflow-state/active.md"
        active.unlink()
        current, digest = CONTROLLER.parse_active_workflow(self.root)
        self.assertEqual(current, "none")
        self.assertEqual(digest, CONTROLLER.hashlib.sha256(b"").hexdigest())

        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint --route discovery "
            "--repository-write allowed --verification required"
        )
        self.management(
            "python3 .ai-workflow/runtime/controller.py durable "
            "--target discovery --resolution same"
        )
        output, _changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "editFiles",
                "tool_input": {"files": [".ai-workflow-state/active.md"]},
                "tool_use_id": "first-durable-write",
            },
            self.state,
            self.root,
            "vscode",
        )
        self.assertEqual(output, {})

    def test_invalid_active_state_remains_a_correctness_error(self) -> None:
        active = self.root / ".ai-workflow-state/active.md"
        active.write_text("# Active workflow\n\n- Active workflow: invented\n", encoding="utf-8")
        with self.assertRaisesRegex(CONTROLLER.ControllerError, "invalid Active workflow"):
            CONTROLLER.parse_active_workflow(self.root)

    def test_transient_state_path_remains_outside_the_repository(self) -> None:
        transient = CONTROLLER.state_path(self.root, self.payload, "vscode")
        with self.assertRaises(ValueError):
            transient.relative_to(self.root)
        self.assertNotIn(".ai-workflow-state", transient.parts)

    def test_stop_blocks_once_then_terminates_without_loop(self) -> None:
        self.state["substantive_execution"] = True
        path = CONTROLLER.state_path(self.root, self.payload, "vscode")
        CONTROLLER.save_state(path, self.state)
        first = CONTROLLER.handle_hook(
            {**self.payload, "hook_event_name": "Stop", "stop_hook_active": False},
            "vscode",
        )
        self.assertIn("hookSpecificOutput", first, first)
        self.assertEqual(first["hookSpecificOutput"]["decision"], "block")
        second = CONTROLLER.handle_hook(
            {**self.payload, "hook_event_name": "Stop", "stop_hook_active": True},
            "vscode",
        )
        self.assertEqual(second["continue"], False)
        self.assertIn("route checkpoint", second["stopReason"])
        CONTROLLER.remove_state(path)

    def test_vscode_snake_case_wire_fixture_reaches_controller_gates(self) -> None:
        prompt = {
            **self.payload,
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Make a small direct edit.",
        }
        self.assertEqual(CONTROLLER.handle_hook(prompt, "vscode"), {})

        denied = CONTROLLER.handle_hook(
            {
                **self.payload,
                "hook_event_name": "PreToolUse",
                "tool_name": "editFiles",
                "tool_input": {"files": ["docs/direct.md"]},
                "tool_use_id": "wire-denied",
            },
            "vscode",
        )
        self.assertEqual(
            denied["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

        declaration = {
            **self.payload,
            "hook_event_name": "PreToolUse",
            "tool_name": "run_in_terminal",
            "tool_input": {
                "command": (
                    "python3 .ai-workflow/runtime/controller.py checkpoint --route direct "
                    "--repository-write allowed --verification not-required"
                )
            },
            "tool_use_id": "wire-checkpoint",
        }
        accepted = CONTROLLER.handle_hook(declaration, "vscode")
        self.assertIn("additionalContext", accepted["hookSpecificOutput"])
        self.assertEqual(
            accepted["hookSpecificOutput"]["permissionDecision"],
            "allow",
        )

        allowed = CONTROLLER.handle_hook(
            {
                **self.payload,
                "hook_event_name": "PreToolUse",
                "tool_name": "editFiles",
                "tool_input": {"files": ["docs/direct.md"]},
                "tool_use_id": "wire-allowed",
            },
            "vscode",
        )
        self.assertEqual(allowed, {})
        CONTROLLER.remove_state(CONTROLLER.state_path(self.root, self.payload, "vscode"))

    def test_vscode_command_adapter_emits_checkpoint_approval_on_stdout(self) -> None:
        prompt = subprocess.run(
            [sys.executable, str(CONTROLLER_PATH), "hook", "--host", "vscode"],
            input=json.dumps(
                {
                    **self.payload,
                    "hook_event_name": "UserPromptSubmit",
                    "prompt": "Inspect recent git history.",
                }
            ),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(prompt.returncode, 0, prompt.stderr)
        self.assertEqual(json.loads(prompt.stdout), {})

        checkpoint = subprocess.run(
            [sys.executable, str(CONTROLLER_PATH), "hook", "--host", "vscode"],
            input=json.dumps(
                {
                    **self.payload,
                    "hook_event_name": "PreToolUse",
                    "tool_name": "run_in_terminal",
                    "tool_input": {
                        "command": (
                            "python3 .ai-workflow/runtime/controller.py checkpoint "
                            "--route direct --mode read-only --repository-write denied "
                            "--verification not-required --next-action read-only"
                        )
                    },
                    "tool_use_id": "wire-process-checkpoint",
                }
            ),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(checkpoint.returncode, 0, checkpoint.stderr)
        output = json.loads(checkpoint.stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"],
            "allow",
        )

        terminal = subprocess.run(
            [sys.executable, str(CONTROLLER_PATH), "hook", "--host", "vscode"],
            input=json.dumps(
                {
                    **self.payload,
                    "hook_event_name": "PreToolUse",
                    "tool_name": "run_in_terminal",
                    "tool_input": {"command": "git log -3 --oneline"},
                    "tool_use_id": "wire-process-git-log",
                }
            ),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(terminal.returncode, 0, terminal.stderr)
        self.assertEqual(json.loads(terminal.stdout), {})
        CONTROLLER.remove_state(CONTROLLER.state_path(self.root, self.payload, "vscode"))

    def test_prompt_reset_does_not_inherit_route_and_next_checkpoint_is_approved(self) -> None:
        prompt = {
            **self.payload,
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Inspect recent git history.",
        }
        self.assertEqual(CONTROLLER.handle_hook(prompt, "vscode"), {})

        checkpoint = {
            **self.payload,
            "hook_event_name": "PreToolUse",
            "tool_name": "run_in_terminal",
            "tool_input": {
                "command": (
                    "python3 .ai-workflow/runtime/controller.py checkpoint --route direct "
                    "--mode read-only --repository-write denied --verification not-required "
                    "--next-action read-only"
                )
            },
            "tool_use_id": "prompt-a-checkpoint",
        }
        first = CONTROLLER.handle_hook(checkpoint, "vscode")
        self.assertEqual(first["hookSpecificOutput"]["permissionDecision"], "allow")

        second_prompt = {
            **prompt,
            "prompt": "Now inspect a different part of the repository.",
        }
        self.assertEqual(CONTROLLER.handle_hook(second_prompt, "vscode"), {})
        path = CONTROLLER.state_path(self.root, self.payload, "vscode")
        reset = CONTROLLER.load_state(path, self.root, self.payload, "vscode")
        self.assertIsNone(reset["route"])
        self.assertIsNone(reset["pending_action"])

        second = {**checkpoint, "tool_use_id": "prompt-b-checkpoint"}
        accepted = CONTROLLER.handle_hook(second, "vscode")
        self.assertEqual(accepted["hookSpecificOutput"]["permissionDecision"], "allow")
        current = CONTROLLER.load_state(path, self.root, self.payload, "vscode")
        self.assertEqual(current["route"], "direct")
        CONTROLLER.remove_state(path)

    def test_hosts_with_prompt_context_support_receive_fresh_protocol_guidance(self) -> None:
        for host in ("codex", "claude-code"):
            output = CONTROLLER.handle_hook(
                {
                    **self.payload,
                    "hook_event_name": "UserPromptSubmit",
                    "prompt": "Inspect recent git history.",
                },
                host,
            )
            specific = output["hookSpecificOutput"]
            self.assertEqual(specific["hookEventName"], "UserPromptSubmit")
            self.assertIn("controller.py checkpoint", specific["additionalContext"])
            CONTROLLER.remove_state(CONTROLLER.state_path(self.root, self.payload, host))

        claude_state = CONTROLLER.new_state(self.root, self.payload, "claude-code")
        accepted, changed = CONTROLLER.handle_pre_tool(
            {
                **self.payload,
                "tool_name": "Bash",
                "tool_input": {
                    "command": (
                        "python3 .ai-workflow/runtime/controller.py checkpoint --route direct "
                        "--mode read-only --repository-write denied --verification not-required"
                    )
                },
                "tool_use_id": "claude-checkpoint",
            },
            claude_state,
            self.root,
            "claude-code",
        )
        self.assertTrue(changed)
        self.assertEqual(accepted["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_stop_generated_continuation_does_not_reset_turn_state(self) -> None:
        self.state["route"] = "implement"
        self.state["repository_changed"] = True
        self.state["verification"] = {"requirement": "required", "evidence": []}
        self.state["stop_blocks"] = 1
        path = CONTROLLER.state_path(self.root, self.payload, "codex")
        self.state["host"] = "codex"
        CONTROLLER.save_state(path, self.state)

        output = CONTROLLER.handle_hook(
            {
                **self.payload,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Agentic Workflow completion gate: required verification is missing.",
            },
            "codex",
        )

        self.assertEqual(output, {})
        preserved = CONTROLLER.load_state(path, self.root, self.payload, "codex")
        self.assertEqual(preserved["route"], "implement")
        self.assertEqual(preserved["stop_blocks"], 1)
        CONTROLLER.remove_state(path)

    def test_transient_state_contains_no_prompt_or_tool_content(self) -> None:
        prompt = "Please inspect SECRET-PROMPT-TEXT /wayfinder"
        invoked = CONTROLLER.provider_invocations(prompt, self.root, "vscode")
        self.state["user_invoked_providers"] = invoked
        self.management(
            "python3 .ai-workflow/runtime/controller.py checkpoint "
            "--route wayfinder --verification not-required --provider wayfinder"
        )
        serialized = json.dumps(self.state, sort_keys=True)
        self.assertNotIn("SECRET-PROMPT-TEXT", serialized)
        self.assertNotIn("Please inspect", serialized)


if __name__ == "__main__":
    unittest.main()
