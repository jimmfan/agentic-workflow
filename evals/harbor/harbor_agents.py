"""Harbor Codex variants for the paired Agentic Workflow evaluation.

Both conditions use Harbor's built-in Codex implementation unchanged.  These
subclasses add preflight assertions; the workflow condition additionally runs
the checked-in product's supported lifecycle installer in the task workspace.
"""

from __future__ import annotations

import hashlib
import json
import os
import shlex
from pathlib import Path

from harbor.agents.installed.codex import Codex
from harbor.environments.base import BaseEnvironment, ExecResult


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PACKAGE = REPOSITORY_ROOT / "skills" / "agentic-workflow"
REMOTE_PACKAGE = "/tmp/agentic-workflow-package"
GH_CLI = (
    REPOSITORY_ROOT
    / "evals/harbor/cache/tools/gh_2.97.0_linux_arm64/bin/gh"
)
GH_CLI_SHA256 = "ccbb0f14178faefac1cb0f336a853071fa63a1d0df23ef5ab7a304fe3859e082"
REMOTE_TOOL_DIR = "/tmp/agentic-workflow-tools"
REMOTE_GH_CLI = f"{REMOTE_TOOL_DIR}/gh"
WORKSPACE = "/app"
MANAGED_MARKER = "<!-- ai-workflow:managed-begin -->"


def _render_result(label: str, result: ExecResult) -> str:
    return "\n".join(
        [
            f"## {label}",
            f"return_code={result.return_code}",
            "stdout:",
            result.stdout or "",
            "stderr:",
            result.stderr or "",
            "",
        ]
    )


class _EvaluationCodex(Codex):
    """Codex with auditable checks around the experimental condition."""

    condition = "unspecified"

    async def _assert_clean_workspace(self, environment: BaseEnvironment) -> ExecResult:
        command = """
set -eu
for path in \
  /app/.ai-workflow \
  /app/.ai-workflow-state \
  /app/.agents/skills/workflow-debugging \
  /app/.agents/skills/workflow-discovery \
  /app/.agents/skills/workflow-implementation \
  /app/.agents/skills/workflow-verification
do
  if [ -e "$path" ] || [ -L "$path" ]; then
    echo "unexpected Agentic Workflow path: $path" >&2
    exit 1
  fi
done
for file in /app/AGENTS.md /app/CLAUDE.md
do
  if [ -f "$file" ] && grep -Fq '<!-- ai-workflow:managed-begin -->' "$file"; then
    echo "unexpected Agentic Workflow marker: $file" >&2
    exit 1
  fi
done
echo "clean: Agentic Workflow is absent"
""".strip()
        return await self.exec_as_agent(environment, command=command)

    def _write_setup_proof(self, *sections: str) -> None:
        proof_path = self.logs_dir / "setup" / "condition-proof.txt"
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        proof_path.write_text(
            f"condition={self.condition}\n" + "\n".join(sections),
            encoding="utf-8",
        )


class VanillaCodex(_EvaluationCodex):
    """Condition A: built-in Harbor Codex with no workflow installation."""

    condition = "A-vanilla"

    async def setup(self, environment: BaseEnvironment) -> None:
        before = await self._assert_clean_workspace(environment)
        await super().setup(environment)
        after = await self._assert_clean_workspace(environment)
        self._write_setup_proof(
            _render_result("before Codex setup", before),
            _render_result("after Codex setup", after),
        )


class AgenticWorkflowCodex(_EvaluationCodex):
    """Condition B: built-in Harbor Codex plus checked-in Agentic Workflow."""

    condition = "B-agentic-workflow"

    def __init__(self, *args, source_revision: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not source_revision or any(c not in "0123456789abcdef" for c in source_revision):
            raise ValueError("source_revision must be a lowercase hexadecimal Git commit")
        self.source_revision = source_revision

    async def setup(self, environment: BaseEnvironment) -> None:
        before = await self._assert_clean_workspace(environment)
        await super().setup(environment)

        if not WORKFLOW_PACKAGE.is_dir():
            raise RuntimeError(f"missing workflow package: {WORKFLOW_PACKAGE}")
        if not GH_CLI.is_file():
            raise RuntimeError(
                f"missing pinned Linux/arm64 GitHub CLI evaluation tool: {GH_CLI}"
            )
        gh_digest = hashlib.sha256(GH_CLI.read_bytes()).hexdigest()
        if gh_digest != GH_CLI_SHA256:
            raise RuntimeError(
                "pinned Linux/arm64 GitHub CLI checksum does not match the "
                "evaluation manifest"
            )
        gh_token = os.environ.get("HARBOR_EVAL_GH_TOKEN", "").strip()
        if not gh_token:
            raise RuntimeError(
                "condition B requires authenticated GitHub CLI access for the "
                "normal provider lifecycle"
            )

        await environment.upload_dir(WORKFLOW_PACKAGE, REMOTE_PACKAGE)
        await self.exec_as_root(
            environment,
            command=f"install -d -m 0755 {shlex.quote(REMOTE_TOOL_DIR)}",
        )
        await environment.upload_file(GH_CLI, REMOTE_GH_CLI)
        await self.exec_as_root(
            environment,
            command=f"chmod 0755 {shlex.quote(REMOTE_GH_CLI)}",
        )
        gh_version = await self.exec_as_agent(
            environment,
            command=f"{shlex.quote(REMOTE_GH_CLI)} --version",
        )
        lifecycle = f"{REMOTE_PACKAGE}/scripts/lifecycle.py"
        try:
            install = await self.exec_as_agent(
                environment,
                command=(
                    f"PATH={shlex.quote(REMOTE_TOOL_DIR)}:$PATH "
                    f"python3 {shlex.quote(lifecycle)} "
                    f"--source-revision {shlex.quote(self.source_revision)} "
                    f"install {shlex.quote(WORKSPACE)}"
                ),
                env={"GH_TOKEN": gh_token},
            )
        finally:
            cleanup = await self.exec_as_root(
                environment,
                command=(
                    f"rm -f {shlex.quote(REMOTE_GH_CLI)}\n"
                    f"rmdir {shlex.quote(REMOTE_TOOL_DIR)}"
                ),
            )
        status = await self.exec_as_agent(
            environment,
            command=f"python3 {shlex.quote(lifecycle)} status {shlex.quote(WORKSPACE)}",
        )
        source_cleanup = await self.exec_as_root(
            environment,
            command=f"rm -rf {shlex.quote(REMOTE_PACKAGE)}",
        )
        self._write_setup_proof(
            _render_result("before Codex setup", before),
            _render_result("transient GitHub CLI", gh_version),
            _render_result("workflow install", install),
            _render_result("workflow status", status),
            _render_result("transient GitHub CLI cleanup", cleanup),
            _render_result("transient workflow source cleanup", source_cleanup),
        )
        proof = await self.exec_as_agent(
            environment,
            command=(
                "set -eu\n"
                "test -f /app/.ai-workflow/install-manifest.json\n"
                "grep -Fq '<!-- ai-workflow:managed-begin -->' /app/AGENTS.md\n"
                "test -f /app/.agents/skills/workflow-debugging/SKILL.md\n"
                "test -f /app/.agents/skills/workflow-discovery/SKILL.md\n"
                "test -f /app/.agents/skills/workflow-implementation/SKILL.md\n"
                "test -f /app/.agents/skills/workflow-verification/SKILL.md\n"
                f"test ! -e {shlex.quote(REMOTE_GH_CLI)}\n"
                f"test ! -e {shlex.quote(REMOTE_PACKAGE)}\n"
                "python3 -c 'import json; p=json.load(open(\"/app/.ai-workflow/install-manifest.json\")); "
                "print(json.dumps({\"source_revision\": p.get(\"source_revision\"), "
                "\"framework_version\": p.get(\"framework_version\")}, sort_keys=True))'\n"
                "python3 - <<'PY'\n"
                "import json\n"
                "from pathlib import Path\n"
                "\n"
                "workspace = Path('/app')\n"
                "declaration = json.loads(\n"
                "    (workspace / '.ai-workflow/providers.json').read_text(encoding='utf-8')\n"
                ")\n"
                "provider_names = [item['name'] for item in declaration['provider']['skills']]\n"
                "provider_repository = declaration['provider']['repository']\n"
                "provider_version = declaration['provider']['version']\n"
                "missing = [\n"
                "    name\n"
                "    for name in provider_names\n"
                "    if not (workspace / '.agents/skills' / name / 'SKILL.md').is_file()\n"
                "]\n"
                "if missing:\n"
                "    raise SystemExit(\n"
                "        'condition B rejected: missing declared providers: ' + ', '.join(missing)\n"
                "    )\n"
                "pin_errors = []\n"
                "for item in declaration['provider']['skills']:\n"
                "    skill_text = (\n"
                "        workspace / '.agents/skills' / item['name'] / 'SKILL.md'\n"
                "    ).read_text(encoding='utf-8')\n"
                "    expected_metadata = (\n"
                "        f'github-path: {item[\"path\"]}',\n"
                "        f'github-pinned: {provider_version}',\n"
                "        f'github-ref: refs/tags/{provider_version}',\n"
                "        f'github-repo: https://github.com/{provider_repository}',\n"
                "    )\n"
                "    absent_metadata = [\n"
                "        value for value in expected_metadata if value not in skill_text\n"
                "    ]\n"
                "    if absent_metadata:\n"
                "        pin_errors.append(f'{item[\"name\"]}: {absent_metadata}')\n"
                "if pin_errors:\n"
                "    raise SystemExit(\n"
                "        'condition B rejected: provider pin mismatch: ' + '; '.join(pin_errors)\n"
                "    )\n"
                "\n"
                "installed_roots = [workspace / '.ai-workflow']\n"
                "installed_roots.extend(\n"
                "    workspace / '.agents/skills' / name\n"
                "    for name in provider_names\n"
                ")\n"
                "installed_roots.extend(\n"
                "    workspace / '.agents/skills' / name\n"
                "    for name in (\n"
                "        'workflow-debugging',\n"
                "        'workflow-discovery',\n"
                "        'workflow-implementation',\n"
                "        'workflow-verification',\n"
                "    )\n"
                ")\n"
                "python_files = sorted(\n"
                "    str(path.relative_to(workspace))\n"
                "    for root in installed_roots\n"
                "    for path in root.rglob('*.py')\n"
                ")\n"
                "if python_files:\n"
                "    raise SystemExit(\n"
                "        'condition B rejected: Agentic Workflow Python contamination: '\n"
                "        + ', '.join(python_files)\n"
                "    )\n"
                "print(json.dumps({\n"
                "    'declared_providers_present': len(provider_names),\n"
                "    'declared_providers_missing': 0,\n"
                "    'provider_pin': f'{provider_repository}@{provider_version}',\n"
                "    'workflow_python_files': python_files,\n"
                "}, sort_keys=True))\n"
                "PY"
            ),
        )

        for label, result in (
            ("workflow install", install),
            ("workflow status", status),
            ("workflow presence and contamination proof", proof),
            ("transient GitHub CLI cleanup", cleanup),
            ("transient workflow source cleanup", source_cleanup),
            ("transient GitHub CLI version", gh_version),
        ):
            if result.return_code != 0:
                raise RuntimeError(
                    f"condition B setup failed during {label}: "
                    f"{result.stderr or result.stdout}"
                )

        manifest_line = next(
            line
            for line in (proof.stdout or "").splitlines()
            if '"source_revision"' in line
        )
        manifest = json.loads(manifest_line)
        if manifest.get("source_revision") != self.source_revision:
            raise RuntimeError(
                "installed source revision does not match the frozen evaluation revision"
            )

        self._write_setup_proof(
            _render_result("before Codex setup", before),
            _render_result("transient GitHub CLI", gh_version),
            _render_result("workflow install", install),
            _render_result("workflow status", status),
            _render_result("workflow presence proof", proof),
            _render_result("transient GitHub CLI cleanup", cleanup),
            _render_result("transient workflow source cleanup", source_cleanup),
        )
