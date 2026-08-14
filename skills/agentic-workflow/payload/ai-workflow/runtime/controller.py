#!/usr/bin/env python3
"""Host-neutral lifecycle controller for Agentic Workflow hook adapters.

The controller records only compact orchestration metadata in the operating
system temporary directory. It never stores prompts, tool arguments, tool
responses, source code, or credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import tempfile
import time
from typing import Any, Mapping, MutableMapping, Optional, Sequence


SCHEMA_VERSION = 1
MINIMUM_PYTHON = (3, 11)
PROVIDER_PATH = Path(".ai-workflow/providers.json")
ACTIVE_STATE_PATH = Path(".ai-workflow-state/active.md")
PROTECTED_PATHS = (
    ".ai-workflow/runtime/",
    ".github/hooks/agentic-workflow.json",
)
ROUTE = re.compile(r"[a-z][a-z0-9-]*(?: → [a-z][a-z0-9-]*)*")
SAFE_VALUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}")
ACTIVE_WORKFLOWS = {
    "discovery",
    "implementation",
    "debugging",
    "verification",
    "provider",
    "none",
}
HOST_ALIASES = {
    "vscode": "github-copilot",
    "github-copilot-vscode": "github-copilot",
    "copilot-cli": "github-copilot",
    "copilot-cloud": "github-copilot",
    "codex": "codex",
    "claude-code": "claude-code",
}
EVENT_ALIASES = {
    "sessionStart": "SessionStart",
    "userPromptSubmitted": "UserPromptSubmit",
    "userPromptSubmit": "UserPromptSubmit",
    "preToolUse": "PreToolUse",
    "postToolUse": "PostToolUse",
    "agentStop": "Stop",
    "stop": "Stop",
}
READ_TOOL_MARKERS = (
    "read",
    "search",
    "grep",
    "find",
    "list",
    "view",
    "inspect",
    "fetch",
    "websearch",
    "openfile",
    "getfile",
)
READ_TOOL_NAMES = {"read"}
NEUTRAL_TOOL_MARKERS = ("think", "todo", "plan", "question", "subagent")
WRITE_TOOL_MARKERS = (
    "applypatch",
    "editfile",
    "editfiles",
    "createfile",
    "writefile",
    "replacefile",
    "replacestring",
    "deletefile",
    "movefile",
    "renamefile",
    "editintofile",
    "notebookedit",
)
WRITE_TOOL_NAMES = {"edit", "write", "delete", "move", "rename"}
SHELL_TOOL_MARKERS = ("terminal", "shell", "bash", "execcommand", "runcommand")
MANAGEMENT_SHELL_TOOLS = {"bash", "runinterminal", "runterminalcommand"}
ACTION_KINDS = {
    "read-only",
    "external-read",
    "repository-write",
    "external-mutation",
    "destructive",
}


class ControllerError(RuntimeError):
    """A declared transition or hook input violates the controller contract."""


def require_supported_python() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        found = ".".join(str(part) for part in sys.version_info[:3])
        raise ControllerError(f"Python 3.11 or newer is required; found Python {found}")


def compact_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:24]


def json_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return compact_hash(encoded)


def project_root(payload: Mapping[str, object]) -> Path:
    raw = payload.get("cwd")
    candidate = Path(raw) if isinstance(raw, str) and raw else Path.cwd()
    try:
        resolved = candidate.resolve()
    except OSError as error:
        raise ControllerError(f"cannot resolve hook working directory: {error}") from error
    if not resolved.is_dir():
        raise ControllerError(f"hook working directory is not a directory: {resolved}")
    for candidate in (resolved, *resolved.parents):
        if plain_project_file(candidate, PROVIDER_PATH) or plain_project_file(
            candidate, Path(".ai-workflow/runtime/controller.py")
        ):
            return candidate
    return resolved


def session_identity(payload: Mapping[str, object]) -> str:
    for field in ("session_id", "transcript_path"):
        value = payload.get(field)
        if isinstance(value, str) and value:
            return value
    return "host-did-not-supply-session-identity"


def state_path(root: Path, payload: Mapping[str, object], host: str) -> Path:
    getuid = getattr(os, "getuid", None)
    user_identity = f"uid:{getuid()}" if callable(getuid) else f"home:{Path.home()}"
    base = Path(tempfile.gettempdir()) / (
        "agentic-workflow-controller-" + compact_hash(user_identity)
    )
    project = compact_hash(str(root))
    session = compact_hash(f"{host}:{session_identity(payload)}")
    return base / project / f"{session}.json"


def new_state(root: Path, payload: Mapping[str, object], host: str) -> MutableMapping[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "project": compact_hash(str(root)),
        "session": compact_hash(session_identity(payload)),
        "host": host,
        "route": None,
        "mode": "normal",
        "authorization": {
            "repository_write": "denied",
            "external_mutation": "denied",
            "destructive": "denied",
        },
        "verification": {"requirement": "unspecified", "evidence": []},
        "selected_providers": [],
        "provider_outcomes": {},
        "user_invoked_providers": [],
        "pending_action": None,
        "tools": {},
        "last_successful_tool": None,
        "substantive_execution": False,
        "repository_changed": False,
        "durable_grant": None,
        "stop_blocks": 0,
        "updated_at": int(time.time()),
    }


def load_state(path: Path, root: Path, payload: Mapping[str, object], host: str) -> MutableMapping[str, object]:
    if path.is_symlink() or path.parent.is_symlink() or path.parent.parent.is_symlink():
        raise ControllerError("refusing symlinked transient controller state")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return new_state(root, payload, host)
    except (OSError, json.JSONDecodeError) as error:
        raise ControllerError(f"cannot read transient controller state: {error}") from error
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise ControllerError("transient controller state has an unsupported schema")
    if value.get("project") != compact_hash(str(root)) or value.get("host") != host:
        raise ControllerError("transient controller state identity does not match this hook")
    return value


def save_state(path: Path, state: MutableMapping[str, object]) -> None:
    base = path.parent.parent
    if base.exists() and (base.is_symlink() or not base.is_dir()):
        raise ControllerError("transient controller base must be a regular directory")
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(base, 0o700)
    except OSError:
        pass
    if path.parent.exists() and (path.parent.is_symlink() or not path.parent.is_dir()):
        raise ControllerError("transient project state must be a regular directory")
    path.parent.mkdir(exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ControllerError("refusing symlinked transient controller state")
    try:
        os.chmod(path.parent, 0o700)
    except OSError:
        pass
    state["updated_at"] = int(time.time())
    descriptor, temporary_name = tempfile.mkstemp(prefix="state-", suffix=".json", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(state, stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def remove_state(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def load_provider_contract(
    root: Path,
) -> tuple[dict[str, Mapping[str, object]], Mapping[str, object], Mapping[str, object]]:
    path = root / PROVIDER_PATH
    if not plain_project_file(root, PROVIDER_PATH):
        raise ControllerError("provider declaration must be a regular non-symlink file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ControllerError(f"provider declaration is unavailable or invalid: {error}") from error
    provider = value.get("provider") if isinstance(value, dict) else None
    hosts = value.get("hosts") if isinstance(value, dict) else None
    configuration = value.get("configuration") if isinstance(value, dict) else None
    skills = provider.get("skills") if isinstance(provider, dict) else None
    if not isinstance(skills, list) or not isinstance(hosts, dict) or not isinstance(configuration, dict):
        raise ControllerError("provider declaration does not contain skills, hosts, and configuration")
    result: dict[str, Mapping[str, object]] = {}
    for item in skills:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("name"), str)
            or re.fullmatch(r"[a-z0-9][a-z0-9-]*", item["name"]) is None
        ):
            raise ControllerError("provider declaration contains an invalid skill record")
        result[item["name"]] = item
    return result, hosts, configuration


def plain_project_file(root: Path, relative: Path) -> bool:
    if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
        return False
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return False
    return current.is_file()


def provider_prerequisite_failures(
    root: Path,
    skill: Mapping[str, object],
    configuration: Mapping[str, object],
) -> list[str]:
    required = skill.get("requires_configuration")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise ControllerError("provider skill has invalid prerequisite metadata")
    failures = []
    for name in required:
        record = configuration.get(name)
        raw_path = record.get("path") if isinstance(record, dict) else None
        if (
            not isinstance(raw_path, str)
            or not raw_path
            or "\\" in raw_path
            or not plain_project_file(root, Path(raw_path))
        ):
            failures.append(name)
            continue
        try:
            if not (root / raw_path).read_bytes().strip():
                failures.append(name)
        except OSError:
            failures.append(name)
    return failures


def command_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, exit_on_error=False)
    subparsers = parser.add_subparsers(dest="operation", required=True)

    checkpoint = subparsers.add_parser("checkpoint", add_help=False, exit_on_error=False)
    checkpoint.add_argument("--route", required=True)
    checkpoint.add_argument(
        "--mode", choices=("normal", "diagnosis", "review", "read-only"), default="normal"
    )
    checkpoint.add_argument("--repository-write", choices=("allowed", "denied"), default="denied")
    checkpoint.add_argument("--external-mutation", choices=("allowed", "denied"), default="denied")
    checkpoint.add_argument("--destructive", choices=("allowed", "denied"), default="denied")
    checkpoint.add_argument(
        "--verification", choices=("required", "not-required", "unspecified"), default="unspecified"
    )
    checkpoint.add_argument("--provider", action="append", default=[])
    checkpoint.add_argument("--next-action", choices=sorted(ACTION_KINDS))

    action = subparsers.add_parser("action", add_help=False, exit_on_error=False)
    action.add_argument("--kind", choices=sorted(ACTION_KINDS), required=True)

    provider = subparsers.add_parser("provider", add_help=False, exit_on_error=False)
    provider.add_argument("--name", required=True)
    provider.add_argument(
        "--outcome",
        choices=("started", "executed", "handoff", "unavailable", "blocked"),
        required=True,
    )

    evidence = subparsers.add_parser("evidence", add_help=False, exit_on_error=False)
    evidence.add_argument("--kind", required=True)
    evidence.add_argument("--result", choices=("passed", "failed", "blocked", "skipped"), required=True)
    evidence.add_argument("--satisfies", choices=("yes", "no"), default="no")

    limitation = subparsers.add_parser("limitation", add_help=False, exit_on_error=False)
    limitation.add_argument("--reason", required=True)
    limitation.add_argument("--authorized", choices=("yes", "no"), required=True)

    durable = subparsers.add_parser("durable", add_help=False, exit_on_error=False)
    durable.add_argument("--target", choices=sorted(ACTIVE_WORKFLOWS), required=True)
    durable.add_argument(
        "--resolution", choices=("same", "complete", "interrupt", "supersede"), required=True
    )
    return parser


def management_argv(command: str) -> Optional[list[str]]:
    # This is intentionally a tiny declaration grammar, not a shell parser. A
    # command with any shell control/expansion syntax must remain an ordinary
    # opaque action and must never inherit the declaration auto-approval.
    if any(character in command for character in "\n\r\x00;&|<>`$(){}*?[]!#"):
        return None
    try:
        values = shlex.split(command, posix=os.name != "nt")
    except ValueError:
        return None
    if not values:
        return None
    index = 0
    executable = values[index].strip('"').lower()
    if executable in {"py", "py.exe"}:
        index += 1
        if index < len(values) and values[index] == "-3":
            index += 1
    elif executable in {"python", "python3", "python.exe", "python3.exe"}:
        index += 1
    else:
        return None
    if index >= len(values):
        return None
    controller = values[index].replace("\\", "/").strip('"')
    if controller not in {
        ".ai-workflow/runtime/controller.py",
        "./.ai-workflow/runtime/controller.py",
    }:
        return None
    return values[index + 1 :]


def command_candidates(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if not isinstance(value, dict):
        return []
    candidates = []
    for key in ("command", "cmd", "script"):
        item = value.get(key)
        if isinstance(item, str):
            candidates.append(item)
    return candidates if len(candidates) == 1 else []


def parse_management(tool_input: object) -> Optional[argparse.Namespace]:
    for command in command_candidates(tool_input):
        values = management_argv(command)
        if values is None:
            continue
        try:
            return command_parser().parse_args(values)
        except (argparse.ArgumentError, SystemExit):
            raise ControllerError("invalid Agentic Workflow controller declaration")
    return None


def is_management_shell_tool(tool_name: object) -> bool:
    return normalize_tool_name(tool_name) in MANAGEMENT_SHELL_TOOLS


def parse_active_workflow(root: Path) -> tuple[str, str]:
    path = root / ACTIVE_STATE_PATH
    if not path.exists() and not path.is_symlink():
        return "none", hashlib.sha256(b"").hexdigest()
    if not plain_project_file(root, ACTIVE_STATE_PATH):
        raise ControllerError("durable active state must be a regular non-symlink file")
    try:
        data = path.read_bytes()
        text = data.decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ControllerError(f"cannot validate durable active state: {error}") from error
    matches = re.findall(r"^- Active workflow: ([a-z-]+)$", text, flags=re.MULTILINE)
    if len(matches) != 1 or matches[0] not in ACTIVE_WORKFLOWS:
        raise ControllerError("durable active state has an invalid Active workflow field")
    return matches[0], hashlib.sha256(data).hexdigest()


def apply_management(
    args: argparse.Namespace,
    state: MutableMapping[str, object],
    root: Path,
    host: str,
) -> str:
    operation = args.operation
    if operation == "checkpoint":
        if ROUTE.fullmatch(args.route) is None:
            raise ControllerError("route must use compact lowercase labels separated by →")
        if args.mode in {"diagnosis", "review", "read-only"} and args.repository_write != "denied":
            raise ControllerError(f"{args.mode} mode cannot authorize repository writes")
        route_labels = args.route.split(" → ")
        try:
            skills, _hosts, _configuration = load_provider_contract(root)
        except ControllerError:
            skills = {}
        derived = [
            name
            for name in skills
            if any(
                label == name
                or label in {f"{name}-handoff", f"{name}-unavailable", f"{name}-blocked"}
                for label in route_labels
            )
        ]
        provider_names = list(dict.fromkeys([*derived, *args.provider]))
        invalid = [
            name
            for name in provider_names
            if re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) is None
        ]
        if invalid:
            raise ControllerError("route selected invalid provider name(s): " + ", ".join(invalid))
        unknown = [name for name in provider_names if skills and name not in skills]
        if unknown:
            raise ControllerError("route selected undeclared provider skill(s): " + ", ".join(unknown))
        state["route"] = args.route
        state["mode"] = args.mode
        state["authorization"] = {
            "repository_write": args.repository_write,
            "external_mutation": args.external_mutation,
            "destructive": args.destructive,
        }
        state["verification"] = {"requirement": args.verification, "evidence": []}
        state["selected_providers"] = provider_names
        state["provider_outcomes"] = {}
        state["pending_action"] = args.next_action
        return f"route checkpoint recorded: {args.route}"

    if not state.get("route"):
        raise ControllerError("record a route checkpoint before declaring lifecycle transitions")

    if operation == "action":
        state["pending_action"] = args.kind
        return f"next opaque action declared: {args.kind}"

    if operation == "provider":
        selected = state.get("selected_providers")
        if not isinstance(selected, list) or args.name not in selected:
            raise ControllerError(f"provider {args.name!r} was not selected at the route checkpoint")
        if args.outcome == "started":
            skills, hosts, configuration = load_provider_contract(root)
            skill = skills.get(args.name)
            if not isinstance(skill, dict):
                raise ControllerError(f"provider {args.name!r} is not declared")
            host_key = HOST_ALIASES.get(host, host)
            host_contract = hosts.get(host_key) if isinstance(hosts, dict) else None
            invocation = skill.get("invocation")
            policy = invocation.get(host_key) if isinstance(invocation, dict) else None
            available = (
                isinstance(host_contract, dict)
                and host_contract.get("availability") == "available"
            )
            if not available or policy == "unavailable":
                raise ControllerError(f"provider {args.name!r} is unavailable on {host}")
            if not plain_project_file(
                root, Path(".agents") / "skills" / args.name / "SKILL.md"
            ):
                raise ControllerError(f"provider {args.name!r} is not installed")
            missing = provider_prerequisite_failures(root, skill, configuration)
            if missing:
                raise ControllerError(
                    f"provider {args.name!r} is missing required configuration: "
                    + ", ".join(missing)
                )
            invoked = state.get("user_invoked_providers", [])
            if policy == "user-only" and args.name not in invoked:
                raise ControllerError(
                    f"provider {args.name!r} is user-only and was not explicitly invoked in this prompt"
                )
            if policy not in {"implicit", "user-only"}:
                raise ControllerError(f"provider {args.name!r} has an invalid host invocation policy")
        outcomes = state.setdefault("provider_outcomes", {})
        if not isinstance(outcomes, dict):
            raise ControllerError("transient provider state is invalid")
        if args.outcome == "executed" and outcomes.get(args.name) != "started":
            raise ControllerError(
                f"provider {args.name!r} cannot be recorded executed before a validated started transition"
            )
        outcomes[args.name] = args.outcome
        return f"provider outcome recorded: {args.name}={args.outcome}"

    if operation == "evidence":
        if SAFE_VALUE.fullmatch(args.kind) is None:
            raise ControllerError("evidence kind must be a compact non-sensitive label")
        if args.satisfies == "yes" and args.result != "passed":
            raise ControllerError("only passed evidence can satisfy a verification requirement")
        observed = state.get("last_successful_tool")
        if args.satisfies == "yes" and not isinstance(observed, dict):
            raise ControllerError("satisfying evidence must follow an observed successful tool call")
        if args.satisfies == "yes" and observed.get("kind") not in {"read-only", "external-read"}:
            raise ControllerError(
                "satisfying evidence must reference an observed read/check action, not a mutation"
            )
        verification = state.get("verification")
        if not isinstance(verification, dict) or not isinstance(verification.get("evidence"), list):
            raise ControllerError("transient verification state is invalid")
        record = {
            "kind": args.kind,
            "result": args.result,
            "satisfies": args.satisfies == "yes",
            "tool": observed.get("id") if isinstance(observed, dict) else None,
        }
        verification["evidence"].append(record)
        return f"verification evidence recorded: {args.kind}={args.result}"

    if operation == "limitation":
        if SAFE_VALUE.fullmatch(args.reason) is None:
            raise ControllerError("limitation reason must be a compact non-sensitive code")
        verification = state.get("verification")
        if not isinstance(verification, dict):
            raise ControllerError("transient verification state is invalid")
        verification["limitation"] = {
            "reason": args.reason,
            "authorized": args.authorized == "yes",
        }
        return f"verification limitation recorded: {args.reason}"

    if operation == "durable":
        current, digest = parse_active_workflow(root)
        if current == args.target:
            if args.resolution != "same":
                raise ControllerError("an unchanged durable workflow requires resolution=same")
        elif current == "none":
            if args.resolution != "same":
                raise ControllerError("starting from idle durable state requires resolution=same")
        elif args.resolution == "same":
            raise ControllerError(
                f"durable workflow conflict: active={current}, target={args.target}; "
                "declare complete, interrupt, or supersede"
            )
        state["durable_grant"] = {
            "current": current,
            "target": args.target,
            "resolution": args.resolution,
            "sha256": digest,
        }
        return f"durable transition granted: {current}->{args.target} ({args.resolution})"

    raise ControllerError(f"unsupported controller operation: {operation}")


def normalize_tool_name(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower()) if isinstance(value, str) else ""


def classify_tool(name: object) -> str:
    normalized = normalize_tool_name(name)
    if normalized in WRITE_TOOL_NAMES or any(marker in normalized for marker in WRITE_TOOL_MARKERS):
        return "repository-write"
    if any(marker in normalized for marker in SHELL_TOOL_MARKERS):
        return "opaque"
    if normalized in READ_TOOL_NAMES or any(marker in normalized for marker in READ_TOOL_MARKERS):
        return "read-only"
    if any(marker in normalized for marker in NEUTRAL_TOOL_MARKERS):
        return "neutral"
    return "opaque"


def input_text(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).replace("\\", "/").lower()


def deny(reason: str, host: str) -> Mapping[str, object]:
    if host in {"copilot-cli", "copilot-cloud"}:
        return {"permissionDecision": "deny", "permissionDecisionReason": reason}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def pre_tool_output(
    reason: Optional[str],
    host: str,
    context: Optional[str] = None,
    *,
    approve_internal: bool = False,
) -> Mapping[str, object]:
    if reason:
        return deny(reason, host)
    if approve_internal and host in {"vscode", "claude-code"}:
        output: MutableMapping[str, object] = {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
        if context:
            output["additionalContext"] = context
        return {"hookSpecificOutput": output}
    if context:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": context,
            }
        }
    return {}


def controller_launcher() -> str:
    return "py -3" if os.name == "nt" else "python3"


def protocol_guidance() -> str:
    launcher = controller_launcher()
    return (
        "Agentic Workflow enforcement is active. For every user prompt, choose a semantic route "
        "before substantive tools; `direct` is valid. For a direct read-only terminal task, run "
        f"exactly: `{launcher} .ai-workflow/runtime/controller.py checkpoint --route direct "
        "--mode read-only --repository-write denied --verification not-required --next-action "
        "read-only`. Choose different declared values when the request differs. Before each later "
        f"terminal or opaque action, run `{launcher} .ai-workflow/runtime/controller.py action "
        "--kind <kind>`. Declarations record transient framework metadata only and never expand "
        "user authority."
    )


def missing_checkpoint_reason(kind: str) -> str:
    launcher = controller_launcher()
    opaque = (
        " Append `--next-action <kind>` before retrying this opaque tool."
        if kind == "opaque"
        else ""
    )
    return (
        "Route checkpoint missing. Choose the semantic route (`direct` is valid), then run "
        f"`{launcher} .ai-workflow/runtime/controller.py checkpoint --route '<selected-route>' "
        "--mode normal --repository-write denied --verification unspecified`; replace the declared "
        f"values to match the request.{opaque} Declarations never grant authority."
    )


def validate_authorization(state: Mapping[str, object], kind: str) -> Optional[str]:
    authorization = state.get("authorization")
    if not isinstance(authorization, dict):
        return "authorization checkpoint is invalid"
    mode = state.get("mode")
    if kind == "repository-write" and (
        mode in {"diagnosis", "review", "read-only"}
        or authorization.get("repository_write") != "allowed"
    ):
        return f"repository writes are denied by the {mode} route checkpoint"
    if kind == "external-mutation" and authorization.get("external_mutation") != "allowed":
        return "external mutation was not authorized at the route checkpoint"
    if kind == "destructive" and authorization.get("destructive") != "allowed":
        return "destructive action was not authorized at the route checkpoint"
    return None


def handle_pre_tool(
    payload: Mapping[str, object],
    state: MutableMapping[str, object],
    root: Path,
    host: str,
) -> tuple[Mapping[str, object], bool]:
    tool_input = payload.get("tool_input")
    management = (
        parse_management(tool_input)
        if is_management_shell_tool(payload.get("tool_name"))
        else None
    )
    if management is not None:
        message = apply_management(management, state, root, host)
        return pre_tool_output(
            None,
            host,
            message,
            approve_internal=True,
        ), True

    kind = classify_tool(payload.get("tool_name"))
    if kind not in {"read-only", "neutral"} and not state.get("route"):
        return pre_tool_output(missing_checkpoint_reason(kind), host), False

    effective_kind = kind
    if kind == "opaque":
        declared = state.get("pending_action")
        if declared not in ACTION_KINDS:
            return pre_tool_output(
                "Declare the next opaque tool action with controller.py action --kind <kind>.", host
            ), False
        effective_kind = str(declared)
        state["pending_action"] = None

    reason = validate_authorization(state, effective_kind)
    if reason:
        return pre_tool_output(reason, host), True

    targets = input_text(tool_input)
    if effective_kind == "repository-write":
        if any(path in targets for path in PROTECTED_PATHS):
            return pre_tool_output(
                "Direct edits to the installed controller or active hook are blocked; use the package lifecycle.",
                host,
            ), True
        if ACTIVE_STATE_PATH.as_posix() in targets:
            grant = state.get("durable_grant")
            if not isinstance(grant, dict):
                return pre_tool_output(
                    "Validate and declare the durable active-state transition before editing active.md.",
                    host,
                ), True
            try:
                _active, digest = parse_active_workflow(root)
            except ControllerError as error:
                return pre_tool_output(str(error), host), True
            if grant.get("sha256") != digest:
                state["durable_grant"] = None
                return pre_tool_output(
                    "Durable active state changed after validation; inspect it and declare the transition again.",
                    host,
                ), True
            state["durable_grant"] = None

    tool_id = payload.get("tool_use_id")
    identifier = compact_hash(str(tool_id)) if tool_id is not None else json_hash(
        {"name": payload.get("tool_name"), "time": payload.get("timestamp")}
    )
    tools = state.setdefault("tools", {})
    if isinstance(tools, dict):
        if len(tools) >= 32:
            tools.pop(next(iter(tools)))
        tools[identifier] = {"kind": effective_kind}
    if effective_kind not in {"read-only", "external-read", "neutral"}:
        state["substantive_execution"] = True
    return pre_tool_output(None, host), True


def handle_post_tool(payload: Mapping[str, object], state: MutableMapping[str, object]) -> None:
    if is_management_shell_tool(payload.get("tool_name")) and parse_management(
        payload.get("tool_input")
    ) is not None:
        return
    tool_id = payload.get("tool_use_id")
    identifier = compact_hash(str(tool_id)) if tool_id is not None else json_hash(
        {"name": payload.get("tool_name"), "time": payload.get("timestamp")}
    )
    tools = state.get("tools")
    record = tools.pop(identifier, None) if isinstance(tools, dict) else None
    kind = record.get("kind") if isinstance(record, dict) else classify_tool(payload.get("tool_name"))
    state["last_successful_tool"] = {"id": identifier, "kind": kind}
    if kind == "repository-write":
        state["repository_changed"] = True


def provider_invocations(prompt: object, root: Path, host: str) -> list[str]:
    if not isinstance(prompt, str):
        return []
    try:
        skills, hosts, _configuration = load_provider_contract(root)
    except ControllerError:
        return []
    host_key = HOST_ALIASES.get(host, host)
    host_contract = hosts.get(host_key) if isinstance(hosts, dict) else None
    prefix = host_contract.get("explicit_prefix") if isinstance(host_contract, dict) else None
    if not isinstance(prefix, str) or not prefix:
        return []
    return [
        name
        for name in skills
        if re.search(rf"(?<!\S){re.escape(prefix + name)}(?=\s|$)", prompt)
    ]


def stop_failures(state: Mapping[str, object]) -> list[str]:
    failures = []
    if state.get("substantive_execution") and not state.get("route"):
        failures.append("the route checkpoint is missing")
    verification = state.get("verification")
    requirement = verification.get("requirement") if isinstance(verification, dict) else "unspecified"
    evidence = verification.get("evidence") if isinstance(verification, dict) else []
    limitation = verification.get("limitation") if isinstance(verification, dict) else None
    if state.get("repository_changed") and requirement == "unspecified":
        failures.append("verification relevance is unspecified after a repository change")
    if requirement == "required":
        satisfied = isinstance(evidence, list) and any(
            isinstance(item, dict) and item.get("result") == "passed" and item.get("satisfies") is True
            for item in evidence
        )
        accepted_limitation = isinstance(limitation, dict) and limitation.get("authorized") is True
        if not satisfied and not accepted_limitation:
            failures.append("required verification lacks satisfying passed evidence or an authorized limitation")
    return failures


def handle_hook(payload: Mapping[str, object], host: str) -> Mapping[str, object]:
    event_raw = payload.get("hook_event_name")
    event = EVENT_ALIASES.get(str(event_raw), str(event_raw))
    root = project_root(payload)
    path = state_path(root, payload, host)

    if event == "SessionStart":
        state = new_state(root, payload, host)
        save_state(path, state)
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": protocol_guidance(),
            }
        }

    state = load_state(path, root, payload, host)
    if event == "UserPromptSubmit":
        prompt = payload.get("prompt")
        if (
            state.get("stop_blocks") == 1
            and isinstance(prompt, str)
            and prompt.startswith("Agentic Workflow completion gate:")
        ):
            save_state(path, state)
            return {}
        state = new_state(root, payload, host)
        state["user_invoked_providers"] = provider_invocations(prompt, root, host)
        save_state(path, state)
        if host in {"codex", "claude-code"}:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": protocol_guidance(),
                }
            }
        return {}
    if event == "PreToolUse":
        output, changed = handle_pre_tool(payload, state, root, host)
        if changed:
            save_state(path, state)
        return output
    if event == "PostToolUse":
        handle_post_tool(payload, state)
        save_state(path, state)
        return {}
    if event == "Stop":
        failures = stop_failures(state)
        if not failures:
            remove_state(path)
            return {}
        reason = "Agentic Workflow completion gate: " + "; ".join(failures) + "."
        blocks = state.get("stop_blocks")
        already_active = payload.get("stop_hook_active") is True
        if already_active or (isinstance(blocks, int) and blocks >= 1):
            return {"continue": False, "stopReason": reason}
        state["stop_blocks"] = 1
        save_state(path, state)
        if host in {"copilot-cli", "copilot-cloud", "claude-code", "codex"}:
            return {"decision": "block", "reason": reason}
        return {
            "decision": "block",
            "reason": reason,
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "decision": "block",
                "reason": reason,
            }
        }
    return {}


def read_hook_input() -> Mapping[str, object]:
    raw = sys.stdin.read(1_048_577)
    if len(raw) > 1_048_576:
        raise ControllerError("hook input exceeds 1 MiB")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ControllerError(f"hook input is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ControllerError("hook input must be a JSON object")
    return value


def parse_cli(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=sorted(HOST_ALIASES), default="vscode")
    parser.add_argument("operation", nargs=argparse.REMAINDER)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    require_supported_python()
    values = list(argv or sys.argv[1:])
    if values and values[0] == "hook":
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("hook")
        parser.add_argument("--host", choices=sorted(HOST_ALIASES), default="vscode")
        args = parser.parse_args(values)
        payload: Mapping[str, object] = {}
        try:
            payload = read_hook_input()
            output = handle_hook(payload, args.host)
        except ControllerError as error:
            reason = f"Agentic Workflow controller error: {error}"
            event = EVENT_ALIASES.get(
                str(payload.get("hook_event_name")), str(payload.get("hook_event_name"))
            )
            output = deny(reason, args.host) if event == "PreToolUse" else {
                "continue": False,
                "stopReason": reason,
            }
        print(json.dumps(output, sort_keys=True, separators=(",", ":")))
        return 0
    try:
        command_parser().parse_args(values)
    except (argparse.ArgumentError, SystemExit) as error:
        raise ControllerError("invalid controller declaration") from error
    print("Agentic Workflow declaration accepted; the active host hook records it before execution.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ControllerError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
