# Verification model

`verify_package.py` is the release and adoption gate. It validates required
files, skill metadata, inert payload placement, explicit source-to-target
mappings, version equality, exact checksums, forbidden runtime components, and
package-local links. With `--tests`, it also runs lifecycle integration tests in
temporary Git repositories.

The integration suite covers:

- fresh one-operation install and automatic verification;
- optional dry-run without writes;
- existing `AGENTS.md` preservation and restoration;
- fail-closed conflicts and tamper detection;
- idempotent reinstallation;
- safe updates, retired framework paths, and project-owned seeds;
- safe removal;
- manifest/version/checksum drift;
- path-independent package copies; and
- the downloadable bootstrap path using a local archive fixture.

Static checks cannot prove that a running editor discovered instructions. For
GitHub Copilot, open the installed repository as the workspace root and inspect
Chat Diagnostics or the agent customization view for root `AGENTS.md` and the
seven `.agents/skills` entries. For Codex, start a fresh task in the installed
repository and confirm the root policy and skills are listed in the task
context. These interactive checks are read-only but may add a prompt to the
signed-in product's chat history.

Successful package verification ends with:

```text
OK: distributable package is internally consistent.
```
