"""Harbor Codex variants for the paired Agentic Workflow evaluation.

Both conditions use Harbor's built-in Codex implementation unchanged.  These
subclasses add preflight assertions; the workflow condition additionally runs
the checked-in product's supported lifecycle installer in the task workspace.
"""

from __future__ import annotations

import json
import shlex
from pathlib import Path

from harbor.agents.installed.codex import Codex
from harbor.environments.base import BaseEnvironment, ExecResult


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PACKAGE = REPOSITORY_ROOT / "skills" / "agentic-workflow"
REMOTE_PACKAGE = "/tmp/agentic-workflow-package"
WORKSPACE = "/app"


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
  /app/.agent-workflow \
  /app/.wayfinder \
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
  if [ -f "$file" ] && grep -Fq '<!-- agent-workflow:managed-begin -->' "$file"; then
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

        await environment.upload_dir(WORKFLOW_PACKAGE, REMOTE_PACKAGE)
        lifecycle = f"{REMOTE_PACKAGE}/scripts/lifecycle.py"
        install = await self.exec_as_agent(
            environment,
            command=(
                f"python3 {shlex.quote(lifecycle)} "
                f"--source-revision {shlex.quote(self.source_revision)} "
                f"install {shlex.quote(WORKSPACE)}"
            ),
        )
        status = await self.exec_as_agent(
            environment,
            command=f"python3 {shlex.quote(lifecycle)} status {shlex.quote(WORKSPACE)}",
        )
        proof = await self.exec_as_agent(
            environment,
            command=(
                "set -eu\n"
                "test -f /app/.agent-workflow/install-manifest.json\n"
                "grep -Fq '<!-- agent-workflow:managed-begin -->' /app/AGENTS.md\n"
                "test -f /app/.agents/skills/workflow-debugging/SKILL.md\n"
                "test -f /app/.agents/skills/workflow-discovery/SKILL.md\n"
                "test -f /app/.agents/skills/workflow-implementation/SKILL.md\n"
                "test -f /app/.agents/skills/workflow-verification/SKILL.md\n"
                "python3 -c 'import json; p=json.load(open(\"/app/.agent-workflow/install-manifest.json\")); "
                "print(json.dumps({\"source_revision\": p.get(\"source_revision\"), "
                "\"framework_version\": p.get(\"framework_version\")}, sort_keys=True))'\n"
                "python3 - <<'PY'\n"
                "import json\n"
                "from pathlib import Path\n"
                "\n"
                "workspace = Path('/app')\n"
                "declaration = json.loads(\n"
                "    (workspace / '.agent-workflow/providers.json').read_text(encoding='utf-8')\n"
                ")\n"
                "provider_names = [item['name'] for item in declaration['provider']['skills']]\n"
                "missing = [\n"
                "    name\n"
                "    for name in provider_names\n"
                "    if not (workspace / '.agents/skills' / name / 'SKILL.md').is_file()\n"
                "]\n"
                "if missing:\n"
                "    raise SystemExit(\n"
                "        'condition B rejected: missing declared providers: ' + ', '.join(missing)\n"
                "    )\n"
                "\n"
                "installed_roots = [workspace / '.agent-workflow']\n"
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
                "    'workflow_python_files': python_files,\n"
                "}, sort_keys=True))\n"
                "PY"
            ),
        )

        for label, result in (
            ("workflow install", install),
            ("workflow status", status),
            ("workflow presence and contamination proof", proof),
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
            _render_result("workflow install", install),
            _render_result("workflow status", status),
            _render_result("workflow presence proof", proof),
        )
