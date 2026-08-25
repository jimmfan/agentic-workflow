# Release-tag workflow research

Research date: 2026-08-24. External claims below use GitHub- or Git-owned
primary sources. Initial repository observations were made at
`781af366d388ebd8b31c8a45d5c72346b18220a4`. Before integration, live
`origin/main` had advanced to `7a181d2b200e25d113591abe774a7a88f6a70089`,
already declared package version `0.20.0`, and still had no remote tags.

## Conclusions

1. **Use major version `v7` for both GitHub-authored actions.** The current
   stable releases are [`actions/checkout` v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)
   and [`actions/setup-python` v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0).
   Both projects' current usage documentation selects the corresponding `@v7`
   major ref ([checkout README](https://github.com/actions/checkout/blob/main/README.md),
   [setup-python README](https://github.com/actions/setup-python/blob/main/README.md)).

2. **Create an annotated release tag.** Git distinguishes annotated tags,
   which contain a tagger, date, message, and optional signature, from
   lightweight object labels, and explicitly says annotated tags are meant for
   releases ([`git tag` documentation](https://git-scm.com/docs/git-tag)). The
   proposed unsigned annotated `vX.Y.Z` tag therefore matches Git's intended
   release-tag type; cryptographic signing is a separate feature and is not
   required by the requested behavior.

3. **The minimum declared token permission for pushing a new tag is
   job-scoped `contents: write`.** Creating a Git reference, including a
   `refs/tags/...` reference, requires Contents write permission
   ([GitHub Git-reference API](https://docs.github.com/en/rest/git/refs#create-a-reference)).
   GitHub permits `permissions` at job scope, sets omitted permissions to
   `none`, and recommends least privilege
   ([workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idpermissions),
   [`GITHUB_TOKEN` guidance](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token#modifying-the-permissions-for-the-github_token)).
   Repository tag rules can still reject a push; `contents: write` is the
   minimum token scope, not a bypass for repository policy.

4. **An annotated tag needs a tagger identity, but GitHub's bot identity is not
   uniquely required.** The tag object records a tagger name and email
   ([`git tag` documentation](https://git-scm.com/docs/git-tag)), and Git's
   identity environment/configuration controls identity when creating tag
   objects ([`git` environment documentation](https://git-scm.com/docs/git#Documentation/git.txt-codeGITCOMMITTERNAMEcode)).
   GitHub documents `github-actions[bot]` with
   `41898282+github-actions[bot]@users.noreply.github.com` for authenticated
   Git writes ([checkout's built-in-token example](https://github.com/actions/checkout/blob/main/README.md#push-a-commit-using-the-built-in-token)).

   **Inference:** a runner might already supply or infer a usable identity, so
   that exact bot identity is not a Git protocol requirement. Relying on an
   ambient identity is not deterministic, however. The narrowest readable
   setup is command-scoped and leaves no persistent repository/global config:

   ```sh
   git -c user.name='github-actions[bot]' \
       -c user.email='41898282+github-actions[bot]@users.noreply.github.com' \
       tag -a "$tag" "$GITHUB_SHA" -m "Release $tag"
   ```

   Git documents `-c name=value` as configuration passed only to that command
   ([`git` command options](https://git-scm.com/docs/git#Documentation/git.txt--cltnamegtltvaluegt)).

5. **No materially simpler or safer release mechanism preserves all requested
   behavior.**
   This is a design inference from the constraints and sources above. A
   lightweight tag would remove the identity/message but would discard the
   requested and Git-recommended release annotation. Creating an annotated tag
   through GitHub's REST API requires creating both a tag object and its Git
   reference ([tag-object endpoint](https://docs.github.com/en/rest/git/tags#create-a-tag-object),
   [reference endpoint](https://docs.github.com/en/rest/git/refs#create-a-reference)),
   which is more machinery than Git CLI. A single post-verification job in the
   existing workflow, with full history/tags, strict validation,
   command-scoped identity, a non-force push of only the explicit tag ref, and
   serialized execution remains the smallest coherent design. The remote has
   no historical tags, but `0.20.0` already reached `main` before this workflow.
   Therefore the next intentional version increase—not a retroactive
   `v0.20.0`—will establish the first baseline without backfilling or moving any
   release ref ([live repository tags](https://github.com/jimmfan/agentic-workflow/tags)).

6. **This repository does not currently require action references to be pinned
   to full commit SHAs.** At the researched baseline, the sole workflow used
   `actions/checkout@v4` and `actions/setup-python@v5`
   ([baseline workflow](https://github.com/jimmfan/agentic-workflow/blob/781af366d388ebd8b31c8a45d5c72346b18220a4/.github/workflows/verify.yml)),
   and searches of the source instructions, accepted ADRs, and documentation
   found no full-SHA pinning rule. This is a repository observation, not a claim
   that SHA pinning has no value: GitHub says a full commit SHA is the only
   immutable action reference and its preferred security posture
   ([secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions)).
   Therefore updating the existing major refs to `@v7` is consistent with
   current repository policy; adopting full-SHA pins would be a deliberate
   security-policy improvement rather than compliance with an existing rule.

## Recommendation

Proceed with the proposed one-workflow design. Keep verification read-only and
grant only the release-tag job `contents: write`; create an annotated tag at the
explicit triggering SHA with command-scoped bot identity; push only that tag
without force; and retain the requested version-change, monotonic-version,
existing-tag, success dependency, and concurrency checks. No release service,
GitHub Release, or historical-tag backfill is justified by the evidence. A
small standard-library helper is appropriate only to make the exact production
policy executable in isolated Git repositories during deterministic tests.
