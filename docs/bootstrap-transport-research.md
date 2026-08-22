# Bootstrap transport research: `gh skill` versus the Python archive bootstrap

- Date: 2026-08-17
- GitHub CLI examined: 2.97.0
- Repository branch examined: `skill-updates`

## Recommendation

Keep the custom Python bootstrap for this release. `gh skill` is a promising
future replacement for transport, and it does avoid downloading or enumerating
unrelated repository content when given the exact `skills/agent-workflow`
path. It is not currently an equivalent transport for this package, however.
The immediate archive-limit design remains a separate decision; the narrowest
current-code option is to distinguish package-entry limits from a larger,
streamed whole-archive parsing limit. That transitional design was subsequently
accepted and is recorded in
[ADR-0019](../architecture-decisions/0019-scope-bootstrap-limits-to-the-distributable-package.md).

A package-only GitHub Release asset is the strongest future replacement for
the full-repository source archive, but it is not the smallest safe change now.
This repository has no tags, published Releases, or release-publishing workflow;
the only workflow is the read-only verification gate on pull requests and pushes
to `main`. Adopting release assets would therefore require a release policy and
publisher as well as bootstrap changes, and would either stop supporting
arbitrary branches/commits or retain a second source-archive transport for them.
The scoped member-limit fix remains the practical response to the current
failure. Reconsider a package-only asset when the project establishes real,
tagged releases.

The decisive incompatibility is byte preservation. Agent Workflow contains
other, intentionally inert `SKILL.md` files inside its payload and bundled
provider snapshot. GitHub CLI 2.97.0 injects source metadata into **every** file
whose basename is `SKILL.md` while recursively installing the outer skill, not
only into the outer `skills/agent-workflow/SKILL.md`. The relevant condition
is visible in the versioned
[`installSkill` implementation](https://github.com/cli/cli/blob/v2.97.0/internal/skills/installer/installer.go#L232-L285).
That changes the bundled provider bytes, makes the snapshot checksum fail, and
adds false outer-package provenance to the four workflow skills that
`adopt.py` projects into the target repository.

This was reproduced both from the current checkout with `gh skill install
--from-local` and from the public `skill-updates` branch with an exact-path,
pinned remote install. The remote installed package contained the same 143
tracked files as the branch, but running `lifecycle.py install` from that copy
installed the core and four local workflow skills, then correctly warned that
the optional provider projection could not be installed because
`bundled provider snapshot checksum differs from the declaration`. The package
therefore cannot currently preserve the complete routed provider behavior required by
[ADR-0020](../architecture-decisions/0020-own-the-declared-provider-projection.md).

Do not replace bootstrap with `gh skill` unless either GitHub CLI gains a mode
that injects metadata only into the selected skill's root manifest, or Agentic
Workflow deliberately changes its inert package format so nested skill manifests
are not named `SKILL.md` in transit. The latter is a substantial packaging
change, not a narrow fix for the current bootstrap failure.

## Evidence labels

- **Documented**: stated by first-party GitHub, OpenAI, or GitHub CLI sources.
- **Source-inspected**: established from GitHub CLI 2.97.0 source.
- **Live macOS**: run on this macOS checkout with GitHub CLI 2.97.0.
- **Repository-observed**: established from this checkout and disposable local
  targets.
- **Inferred**: conclusion drawn from the cited evidence.
- **Not live-tested**: no native operating-system run was performed.

## Capability comparison

| Requirement | Current Python bootstrap | `gh skill install/update` plus `adopt.py` | Result |
| --- | --- | --- | --- |
| Ignore unrelated repository growth | Downloads the repository archive, then selects the package | Exact-path **install** resolves the package subtree directly, but **update** rediscovers skills from the full recursive repository tree | Better install scope, but update is still repository-coupled |
| Preserve package bytes | Preserves reviewed archive file bytes | Rewrites every nested `SKILL.md` with outer source metadata | **Blocking incompatibility** |
| Project Codex/Copilot placement | Uses a temporary package and projects runtime skills itself | Both project targets resolve to `.agents/skills` | Equivalent at project scope |
| Immutable source identity passed to lifecycle | Resolves the requested ref to a full commit and passes it as `--source-revision` | Root metadata records ref, path, and package tree SHA, but not the resolved full commit; `adopt.py` does not consume this metadata | Not equivalent without another adapter |
| Explicit ref/version update | `--ref` accepts branch, tag, or full commit for each operation | Pinned installs are skipped by `gh skill update`; unpinned update accepts no target ref and resolves latest release before default branch | Not equivalent |
| Initial failure recovery | Downloads/extracts into a temporary directory before package code runs | Initial install writes files directly into the destination and can leave a partial skill | Python path is safer |
| Update failure recovery | Fresh temporary package plus transactional lifecycle reconciliation | GitHub CLI 2.97.0 stages update content beside the skill and restores the old contents on swap failure | Both have a recovery boundary |
| Resource limits before execution | Bounds compressed bytes, members, each file, and aggregate package bytes; validates paths, modes, and types | Safely joins paths and reads Git tree blobs, but imposes no package file-count, per-file-size, or aggregate-size bound in the installer | Not equivalent security policy |
| One-command adoption | The public command downloads, validates, and invokes lifecycle | `gh skill install` only installs the outer skill; a second Python invocation is required to run `adopt.py`/`lifecycle.py` | Not equivalent |
| Runtime prerequisites | Python 3.11+ and HTTPS | Python 3.11+, GitHub CLI 2.90+, and GitHub API access; private sources additionally require authentication | `gh skill` adds a prerequisite |
| Feature stability | Repository-owned behavior | `gh skill` remains public preview and may change without notice | Custom path is currently more stable |

## What `gh skill` does provide

### Exact subtree installation

**Documented and source-inspected.** The install command accepts an exact path
such as `skills/agent-workflow`; GitHub explicitly recommends exact paths for
large repositories because they avoid a full repository traversal.
[The install manual](https://cli.github.com/manual/gh_skill_install) describes
the syntax and optimization. The implementation looks up the named directory,
obtains its tree SHA, recursively enumerates that subtree, and fetches its blobs;
it does not download the repository archive. See
[`DiscoverSkillByPath`](https://github.com/cli/cli/blob/v2.97.0/internal/skills/discovery/discovery.go#L663-L755)
and
[`DiscoverSkillFiles`](https://github.com/cli/cli/blob/v2.97.0/internal/skills/discovery/discovery.go#L756-L850).

**Live macOS.** This command successfully installed the `main` package at
commit `eb8e425bbfc55426949cbfbe0a7ec6955f210dab` into a disposable custom
directory:

```text
gh skill install jimmfan/agentic-workflow skills/agent-workflow \
  --dir <temporary-directory> --force
```

All 93 files tracked under `skills/agent-workflow` at that `main` commit were
present. The installed root manifest contained `github-repo`, `github-path`,
`github-ref`, and `github-tree-sha` metadata. The installed package's
`verify_package.py` passed, and its `adopt.py install` followed by `status`
produced a healthy core in a disposable target. This older `main` package does
not yet contain the provider snapshot whose checksum exposes the nested rewrite.

### Host paths

**Documented and source-inspected.** GitHub CLI 2.97.0 maps project-scoped Codex
and GitHub Copilot skills to the same `.agents/skills` directory. It maps
user-scoped Copilot skills to `~/.copilot/skills` and user-scoped Codex skills
to `~/.codex/skills`; see the versioned
[agent registry](https://github.com/cli/cli/blob/v2.97.0/internal/skills/registry/registry.go#L35-L75).
GitHub's Copilot documentation agrees that project skills may live in
`.agents/skills` and personal skills in `~/.copilot/skills` or
`~/.agents/skills` ([GitHub Copilot skill locations](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills#creating-and-adding-a-skill)).

Current Codex documentation lists repository `.agents/skills` and user
`$HOME/.agents/skills`, not `~/.codex/skills`
([OpenAI's current Codex skill-location table](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)).
Therefore the shared **project** path required by Agent Workflow is compatible,
but GitHub CLI 2.97.0's Codex **user** path should not be treated as verified
against the current Codex contract. An explicit project `--dir .agents/skills`
would avoid host-registry drift but would not solve the nested metadata rewrite.

### Update behavior

**Documented.** `gh skill update` compares the installed frontmatter tree SHA
with the current remote tree SHA. Pinned skills are skipped unless `--unpin` is
used. Unpinned updates resolve the repository's latest GitHub Release first and
fall back to the default branch only when there is no release. `--force`
re-downloads an otherwise matching skill and overwrites local modifications.
See the [update manual](https://cli.github.com/manual/gh_skill_update) and the
[install version-resolution rules](https://cli.github.com/manual/gh_skill_install).

**Source-inspected.** Update matches the recorded source path, stages a fresh
skill beside the current directory, moves existing entries to a backup, moves
the staged entries into place, and restores the backup on a failed swap. It also
removes stale files by replacing the directory contents. See
[`updateSkillInPlace` and `swapDirectoryContents`](https://github.com/cli/cli/blob/v2.97.0/pkg/cmd/skills/update/update.go#L376-L481).

Update does not reuse the exact-path lookup used by install. It first calls
`DiscoverSkills` for the resolved repository commit, which fetches the full
recursive repository tree, rejects a truncated response, and only then matches
the installed skill's recorded source path
([update discovery](https://github.com/cli/cli/blob/v2.97.0/pkg/cmd/skills/update/update.go#L250-L288),
[repository discovery](https://github.com/cli/cli/blob/v2.97.0/internal/skills/discovery/discovery.go#L507-L603)).
GitHub documents a recursive-tree ceiling of 100,000 entries or 7 MB
([Git Trees API](https://docs.github.com/en/rest/git/trees#get-a-tree)). Thus
`gh skill update` eliminates the present 500-entry archive failure but does not
fully decouple update from unrelated repository growth; a sufficiently large
repository tree will make discovery fail instead of falling back to the exact
recorded package path.

**Live macOS.** A dry-run update of the disposable remote installation found
the package and reported it up to date:

```text
gh skill update agent-workflow --dir <temporary-directory> --dry-run
```

This confirms that the injected metadata is sufficient for normal update
discovery. It does not solve Agent Workflow's versioning contract:

- an unpinned update has no `--ref` option and can switch from default-branch
  tracking to latest-release tracking when the repository starts publishing
  releases;
- `--pin` records the pin but makes normal update skip the skill; advancing to a
  reviewed new tag or commit requires another install/reinstall operation; and
- the injected metadata records the selected ref and package tree SHA, not the
  full resolved commit that current `adopt.py --source-revision` records.

## Byte-preservation failure on the current branch

Agent Workflow's outer skill is intentionally a distribution container. It
contains:

- four inert workflow manifests under `payload/skills/*/SKILL.md`; and
- fourteen pinned provider manifests under
  `provider-snapshots/matt-pocock-skills/skills/*/SKILL.md`.

The current GitHub CLI installer loops through every blob in the selected
subtree and applies `InjectGitHubMetadata` whenever
`filepath.Base(relPath) == "SKILL.md"`, then writes the result. The metadata
injector adds repository, ref, tree SHA, and path to the manifest
([installer](https://github.com/cli/cli/blob/v2.97.0/internal/skills/installer/installer.go#L247-L282),
[metadata injector](https://github.com/cli/cli/blob/v2.97.0/internal/skills/frontmatter/frontmatter.go#L60-L89)).
Because the installer passes the outer selected skill's path and tree SHA, each
nested manifest receives provenance for `skills/agent-workflow`, not for its
actual inner provider or payload identity.

The disposable current-branch installation established these effects:

1. source and installed file counts both equaled 143, so this was content
   mutation rather than omission;
2. every nested manifest received `local-path` metadata in the local test (the
   remote path uses the equivalent GitHub metadata injector);
3. `verify_package.py` rejected the provider snapshot checksum;
4. `lifecycle.py install` left core routing usable but could not project the
   fourteen optional provider skills; and
5. the four projected local workflow manifests retained false metadata pointing
   to the outer package, making them candidates for incorrect future `gh skill
   update` interpretation.

This violates both the provider snapshot integrity contract and the requirement
that installation leave the complete reviewed routing/provider projection
available when the release bytes are valid.

## Security and resource-exhaustion comparison

GitHub CLI's Git-tree transport removes tar traversal, tar special-file, and
whole-repository member-count concerns. Its destination uses a safe-path join,
and it writes fetched blobs as regular mode-0644 files
([installer source](https://github.com/cli/cli/blob/v2.97.0/internal/skills/installer/installer.go#L232-L285)).
Git tree entries also avoid duplicate paths by construction.

It does not preserve the current bootstrap's bounded-resource contract. The
2.97.0 installer receives file sizes from discovery but does not check them,
does not cap the number of package blobs, and does not cap aggregate downloaded
or written bytes. Recursive-tree truncation falls back to a depth-bounded tree
walk, but the only explicit bound in that path is 20 directory levels
([discovery source](https://github.com/cli/cli/blob/v2.97.0/internal/skills/discovery/discovery.go#L756-L850)).

Initial remote installation is also not staged: it creates the destination
directory, fetches each blob, and writes it directly. A network/API/write
failure can therefore leave a partial bootstrap skill. The atomic
staging-and-backup behavior applies to `gh skill update`, not initial install.
By contrast, the current Python bootstrap validates and extracts into a
temporary directory before invoking the transactional lifecycle code.

These gaps do not imply that `gh skill` is generally unsafe; its public contract
warns users to review unverified skill content. They do mean it is not an
equivalent implementation of Agent Workflow's accepted pre-execution limits
and failure boundary.

## Platform and prerequisite assessment

| Platform | Evidence | Assessment |
| --- | --- | --- |
| macOS | Live install, package verification, `adopt.py` projection, status, current-branch incompatibility reproduction, and update dry run with GitHub CLI 2.97.0 | Transport works; current package preservation fails |
| Windows | GitHub CLI officially supports Windows and the inspected implementation uses Go `filepath`/`os` APIs; no native Windows run was performed | **Source-compatible, not live-tested** |
| Linux | GitHub CLI officially supports Linux and the inspected implementation uses Go `filepath`/`os` APIs; no native Linux run was performed | **Source-compatible, not live-tested** |

GitHub's official repository lists macOS, Windows, and Linux support and
first-party installation options
([GitHub CLI platform support](https://github.com/cli/cli#installation)). The
`gh skill` command itself was introduced only in 2.90.0, remains public preview,
and is explicitly subject to change without notice
([2.90.0 release notes](https://github.com/cli/cli/releases/tag/v2.90.0#manage-agent-skills-with-gh-skill-public-preview)).
Using it for public adoption would therefore add GitHub CLI 2.90+ to the
existing Python 3.11+ requirement. A live public-repository install succeeded
with an empty GitHub CLI configuration, so authentication is not a universal
requirement; private sources would still require it. The current Python
bootstrap needs no Git executable or GitHub CLI installation and can fetch this
public repository over HTTPS.

There is no single `gh skill` command that also runs `adopt.py`. A user must run
the install command and then invoke Python from the installed package. Combining
those operations into one physical shell line is platform-specific (`python3`
versus common Windows `py`/`python` launchers and shell-specific conditional
syntax), and it still lacks an automatic, full immutable commit value for
`--source-revision`.

## Other supported GitHub CLI designs

- **`gh release download` with a package-only release asset:** This could avoid
  the whole-repository archive and metadata rewriting, and the command supports
  selecting an asset by pattern and destination
  ([manual](https://cli.github.com/manual/gh_release_download)). It requires a
  new release-asset publication/checksum process, covers releases rather than
  arbitrary `main` commits, and still needs extraction and validation code. See
  the detailed assessment below. No such package asset is currently published.
  It is not simpler for this fix.
- **`gh repo clone` plus sparse checkout:** This adds Git, checkout state, and
  multiple platform-sensitive commands. `gh repo clone` is only the clone
  wrapper; sparse selection remains a Git operation
  ([manual](https://cli.github.com/manual/gh_repo_clone)). It is more machinery
  than the current bounded download.
- **`gh api` over Contents/Trees/Blobs:** This can reproduce the exact-path
  traversal used by `gh skill`, but recursion, byte preservation, limits,
  staging, and revision handoff become custom code again. It offers no simpler
  supported lifecycle contract.
- **Dedicated distribution repository:** It would make the existing archive
  package-only but adds another repository and release synchronization boundary.
  Scoping the current bootstrap's package-member limit is smaller and preserves
  one canonical source repository.

## Package-only GitHub Release asset assessment

### Current repository convention

**Repository-observed and live GitHub query.** `git tag --list` is empty, and
`gh release list --repo jimmfan/agentic-workflow` returned no Releases. The
package declares version `0.13.0`, but no tag or release currently publishes
that version. The sole workflow is `.github/workflows/verify.yml`; it runs
`verify_package.py --tests` on Ubuntu and Windows for pull requests and pushes
to `main`, with `contents: read`. There is no package builder, release trigger,
write permission, asset upload, or publication recovery convention.

This means a Release asset is not merely another download URL. It introduces a
new durable release boundary. In particular, it must define when `VERSION`
becomes a tag, which commit is publishable, whether "latest" may include
prereleases, and who can retry a failed draft. That may be worthwhile when the
project begins publishing stable versions, but doing it only to repair the
500-member regression is disproportionate.

### What the design would look like

If tagged Releases are adopted later, use this narrow model:

1. A release workflow checks out an already-created version tag, verifies that
   the tag, `VERSION`, and resolved commit agree, and runs the normal release
   gate before producing anything.
2. It creates one archive from the tagged `skills/agent-workflow` subtree,
   retaining `skills/agent-workflow` in the archive path so the current
   extraction boundary can recognize it. `git archive` supports selecting a
   subtree and records the referenced commit in its tar metadata; when given a
   commit or tag it also uses the recorded commit time instead of wall-clock
   time ([Git `archive` documentation](https://git-scm.com/docs/git-archive)).
3. The builder fixes the archive name and compression settings, then builds it
   twice in separate temporary directories and requires byte-identical output.
   It emits a SHA-256 sidecar from those final bytes. A regression test should
   assert both reproducibility and that only the package subtree is present.
4. The publisher creates a **draft** for an existing remote tag, uploads the
   archive and checksum without `--clobber`, verifies names, sizes, hashes, and
   package verification from the downloaded candidate, then publishes. GitHub
   recommends draft-first publication for immutable releases; publication then
   locks the associated tag and assets and creates a cryptographically
   verifiable release attestation
   ([immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)).
   `gh release create --verify-tag` prevents an accidental release from silently
   creating a tag at the default branch
   ([CLI manual](https://cli.github.com/manual/gh_release_create)).
   The release job should be the only job granted `contents: write`; GitHub's
   workflow contract identifies that as the permission that allows
   `GITHUB_TOKEN` to create a Release
   ([workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idpermissions)).
5. The consuming bootstrap downloads to a temporary location, checks the
   expected SHA-256 before opening the archive, and then retains the current
   compressed-size, package-member, per-file, aggregate-size, path, duplicate,
   mode, symlink, and special-file checks. It passes the release's immutable tag
   commit to `adopt.py` as the source revision.

The current package has 143 tracked files and 232 tar entries when archived by
`git archive` at `HEAD`, so a package-only artifact is already below the current
500-entry limit. More importantly, unrelated repository growth would never
enter that artifact; the package-specific limit would continue to reject a
genuinely excessive package.

GitHub's release-asset API exposes asset size and a `sha256:` digest, and public
release assets can be downloaded without authentication
([release-assets REST API](https://docs.github.com/en/rest/releases/assets)).
Immutable release attestations can also verify the downloaded local asset with
`gh release verify-asset`
([release integrity](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/verify-release-integrity)).
The bootstrap should still verify an expected digest itself, because requiring
`gh` merely to verify the asset would reintroduce the prerequisite this design
is intended to avoid. Release attestation verification is a useful maintainer
or release-gate check, not the only consumer integrity check.

### Ref and update semantics

A Release asset cleanly supports exact version tags and "latest stable". GitHub
provides a stable direct URL for an uploaded latest-release asset using
`/releases/latest/download/<asset-name>`
([linking to Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases)).
It does **not** provide a package asset for `main`, an arbitrary branch, or an
arbitrary commit unless CI continually publishes mutable development assets.
That would undermine the draft-then-immutable release model and make the word
"release" misleading.

The choices would therefore be:

- change normal install/update from current `main` tracking to the latest
  published stable release, while accepting that unreleased refs need a
  maintainer/development path; or
- use release assets for tags/latest and keep codeload archives for branches and
  commits, creating two transports and two recovery/test matrices.

The first is a legitimate future product decision but a visible semantic
change. The second preserves current flexibility but is more complex than the
scoped archive fix and leaves the 500-member bug relevant on the `main` path.
Publishing a moving `main` asset is not recommended.

### One-line use, platforms, and authentication

Do not make `gh release download` a consumer prerequisite. A public asset has a
normal HTTPS download URL and GitHub documents unauthenticated retrieval for
public resources. The existing Python launcher can therefore remain one command
on macOS, Linux, and Windows and can fetch the asset with the standard library,
then run the same platform-neutral validation and `adopt.py` handoff. Private
repositories would require credentials regardless of transport and are outside
the current unauthenticated public-install contract.

Using `gh release download` directly would add GitHub CLI installation and
authentication/configuration behavior, still require a separate extraction and
Python handoff, and require shell-specific composition to become one line. It
is a useful maintainer command, not a simpler consumer bootstrap.

### Failure, recovery, and security

A package asset improves scope and byte preservation: it contains no unrelated
repository members, and GitHub does not rewrite nested `SKILL.md` bytes while
serving an uploaded asset. It does not eliminate the need for custom bootstrap
code. The consumer still needs bounded download, digest verification, safe
archive parsing, a temporary staging directory, runtime-package validation, and
the transactional lifecycle call.

Publication should fail closed:

- never upload or publish when verification, reproducibility, version/tag, or
  checksum checks fail;
- keep incomplete work as a draft, which GitHub permits editing or deleting
  before immutability applies;
- publish only after downloading and verifying the exact uploaded assets;
- enable repository release immutability, which applies to future Releases and
  prevents asset/tag replacement after publication
  ([enabling immutability](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes));
- never use `gh release upload --clobber` for published artifacts—the CLI warns
  that it deletes the original before uploading the replacement, so an upload
  failure can lose the original
  ([upload manual](https://cli.github.com/manual/gh_release_upload)); and
- grant the publishing job only the repository permission needed to create the
  release/assets, while retaining `contents: read` for ordinary verification.

On the consumer side, a missing release, missing asset/checksum, redirect to an
unexpected host, digest mismatch, invalid archive, or package verification
failure must occur before target mutation. The current temporary extraction and
lifecycle transaction provide the appropriate recovery boundary once the
artifact has passed validation.

### Release-asset recommendation

Do **not** introduce a package-only Release asset solely for this bug. Retain the
custom Python bootstrap and fix its member-limit scope now. The Release design
is preferable to whole-repository archives after the project adopts real tagged
releases because it:

- preserves the composite package byte-for-byte;
- makes unrelated repository growth irrelevant;
- supports immutable tags/assets, checksums, and GitHub release attestations;
- retains the public, no-`gh`, cross-platform one-command consumer path; and
- lets the existing bootstrap security and `adopt.py` projection remain in
  place.

At that milestone, make latest-release assets the public stable channel and
keep arbitrary branch/commit installation explicitly developer-only. Until
then, adding a release publisher and a second ref-resolution policy costs more
than the narrow failure it solves.

## Reconsideration criteria

Re-evaluate `gh skill` as the primary transport when all of the following are
true:

1. nested `SKILL.md` resources can be copied byte-for-byte, or the package has a
   reviewed inert representation that is not rewritten in transit;
2. the selected immutable commit/tree identity can be handed to lifecycle
   reconciliation without shell-specific API plumbing;
3. initial installation has an acceptable partial-failure recovery story;
4. package-level count and size resource bounds are provided by the CLI or are
   deliberately replaced by an accepted security decision;
5. pinned update semantics match Agent Workflow's release policy; and
6. requiring a recent preview GitHub CLI is acceptable for all supported
   adoption environments.

Until then, `gh skill` remains appropriate for maintainer-controlled provider
snapshot refreshes, where its metadata injection is explicitly verified and
removed for provenance comparison, but not for transporting the composite
Agent Workflow bootstrap package to consumers.
