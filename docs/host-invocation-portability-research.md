# Host invocation-policy portability across Agent Skills hosts

Date researched: 2026-08-16

## Practical conclusion

`SKILL.md` instructions are portable, but invocation policy is not part of the
current Agent Skills specification. The specification defines the skill package
and progressive-disclosure model, while invocation control remains a host
extension. [The specification's complete frontmatter table](https://agentskills.io/specification)
contains `name`, `description`, `license`, `compatibility`, `metadata`, and the
experimental `allowed-tools`; it does not define either
`disable-model-invocation` or `allow_implicit_invocation`.

- **[Documented]** Codex uses the optional `agents/openai.yaml` sidecar. Its
  `policy.allow_implicit_invocation` defaults to `true`; `false` prevents prompt-
  matched implicit activation while retaining explicit `$skill` activation.
  [OpenAI's current skills documentation](https://developers.openai.com/codex/skills#optional-metadata)
  documents the behavior, and [OpenAI's source-owned metadata reference](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/references/openai_yaml.md)
  calls the sidecar product-specific machine/harness configuration.
- **[Documented]** Claude Code implements the `SKILL.md` field
  `disable-model-invocation: true` as a host-enforced user-only policy. It hides
  the description from the model, blocks a model attempt to call the skill, and
  tells the model not to reproduce the protected workflow another way; explicit
  `/skill-name` remains available. [Claude Code's invocation-control documentation](https://code.claude.com/docs/en/slash-commands#control-who-invokes-a-skill)
  states all three effects.
- **[Documented, surface-specific]** GitHub Copilot CLI and GitHub Copilot in VS
  Code now document the same `disable-model-invocation` field, defaulting to
  `false`, and manual `/SKILL-NAME` invocation. [The Copilot CLI skills reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#skills-reference)
  and [the VS Code Agent Skills page](https://code.visualstudio.com/docs/agent-customization/agent-skills#_use-skills-as-slash-commands)
  both say `true` disables automatic loading while leaving slash invocation.
- **[Unverified]** No first-party source found in this review says that any
  Copilot surface reads `agents/openai.yaml`. Current GitHub and VS Code
  references enumerate `SKILL.md` fields and skill roots but do not mention that
  sidecar. This is absence of an affirmative contract, not proof that every
  implementation ignores the file. [Copilot CLI's field and location tables](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#skills-reference)
  and [VS Code's field table](https://code.visualstudio.com/docs/agent-customization/agent-skills#_skill-file-format)
  are the applicable first-party references.
- **[Unverified, surface-specific]** GitHub documents automatic skill use for
  Copilot cloud agent and Copilot code review, but the reviewed cloud/code-review
  documentation does not separately establish enforcement of
  `disable-model-invocation`. Do not infer that guarantee from the CLI or VS Code
  documentation without a live test or a cloud-specific contract. [GitHub's
  cloud-agent skills guide](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#how-copilot-uses-agent-skills)
  documents description-based automatic use and a code-review note, while the
  [general product overview](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
  only lists the supported surfaces.

The portability gap is therefore narrower than an earlier "Codex versus every
other host" framing: Claude Code, Copilot CLI, and VS Code converge on the same
`SKILL.md` opt-out field, while Codex retains a product-specific sidecar. A
portable provider currently needs both declarations when it wants the same
user-only behavior in Codex and in the documented Claude/Copilot surfaces.

## Evidence labels

- **Documented**: explicitly stated by a first-party specification,
  documentation page, or source-owned reference.
- **Repository-observed**: directly inspected in this checkout; this is not a
  live host result.
- **Inferred**: a conclusion drawn from linked documented facts.
- **Unverified**: not established by the reviewed first-party sources.
- **Not run**: a proposed live test, with no result claimed.

## Compact compatibility table

| Host or surface | Project skill root documented here | Automatic selection by default | Documented user-only mechanism | Explicit form | `agents/openai.yaml` recognition |
| --- | --- | --- | --- | --- | --- |
| Agent Skills portable contract | Not specified by the format specification | Description-driven activation is the reference lifecycle | None in the standard | Not standardized | Not standardized |
| OpenAI Codex CLI / IDE extension | `.agents/skills` | Yes, by description | `agents/openai.yaml`: `policy.allow_implicit_invocation: false` | `$skill-name` | **Documented** |
| Claude Code | `.claude/skills` | Yes, by description | `SKILL.md`: `disable-model-invocation: true`; host blocks model calls | `/skill-name` | **Not documented; OpenAI identifies it as product-specific** |
| GitHub Copilot CLI | `.agents/skills` (also `.github/skills` and `.claude/skills`) | Yes | `SKILL.md`: `disable-model-invocation: true` | `/SKILL-NAME` | **Unverified / not documented** |
| GitHub Copilot in VS Code | `.agents/skills` (also `.github/skills` and `.claude/skills`) | Yes | `SKILL.md`: `disable-model-invocation: true` | `/skill-name` | **Unverified / not documented** |
| Copilot cloud agent / code review | `.agents/skills` is listed as a project root | Description-based automatic use is documented | **Unverified for these surfaces** | **Not established by the reviewed source** | **Unverified / not documented** |

Table sources: [Agent Skills specification and lifecycle](https://agentskills.io/specification),
[OpenAI Codex skills](https://developers.openai.com/codex/skills),
[Claude Code skill locations and invocation control](https://code.claude.com/docs/en/slash-commands),
[Copilot CLI skills reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#skills-reference),
[VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills),
and [GitHub's cloud-agent skills guide](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills).

## 1. What the portable Agent Skills contract does and does not cover

- **[Documented]** A conforming skill is a directory containing at least a
  `SKILL.md` with YAML frontmatter and Markdown instructions; `scripts/`,
  `references/`, `assets/`, and other directories are allowed. [The Agent Skills
  directory and file specification](https://agentskills.io/specification#directory-structure)
  defines that package shape.
- **[Documented]** The normative frontmatter list has six fields:
  `name`, `description`, `license`, `compatibility`, `metadata`, and
  experimental `allowed-tools`. The `metadata` map is the stated extension point
  for client-specific string properties. [The specification's frontmatter and
  metadata sections](https://agentskills.io/specification#frontmatter) define
  those fields.
- **[Documented]** The reference lifecycle is progressive disclosure: expose
  `name` and `description`, load the full `SKILL.md` when activated, then load
  resources on demand. [The specification's progressive-disclosure section](https://agentskills.io/specification#progressive-disclosure)
  defines the tiers.
- **[Inferred]** Because neither invocation-policy spelling appears in the
  normative field list, cross-host invocation control is outside the current
  portable contract even though multiple clients accept compatible extensions.
  [The complete specification](https://agentskills.io/specification) and
  [Claude Code's explicit distinction between standard fields and its extensions](https://code.claude.com/docs/en/slash-commands#using-skill-frontmatter-outside-claude-code)
  support this conclusion.

## 2. OpenAI Codex: `agents/openai.yaml`

- **[Documented]** Codex discovers repo skills by scanning `.agents/skills`
  from the current working directory through the repository root, and supports
  both prompt-matched implicit activation and explicit `$skill` activation.
  [OpenAI's current Codex skills page](https://developers.openai.com/codex/skills#how-chatgpt-and-codex-use-skills)
  documents activation and [the same page's location table](https://developers.openai.com/codex/skills#where-codex-loads-local-skills)
  documents discovery.
- **[Documented]** The optional sidecar supports `interface` presentation fields
  (`display_name`, `short_description`, small/large icons, `brand_color`, and
  `default_prompt`), MCP tool dependencies, and
  `policy.allow_implicit_invocation`. [OpenAI's optional-metadata section](https://developers.openai.com/codex/skills#optional-metadata)
  gives the current public example, and [the source-owned field reference](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/references/openai_yaml.md)
  describes the fields and constraints.
- **[Documented]** `allow_implicit_invocation` defaults to `true`; setting it to
  `false` removes prompt-matched implicit invocation but preserves explicit
  `$skill` invocation. [OpenAI's public documentation](https://developers.openai.com/codex/skills#optional-metadata)
  and [the current `SkillMetadata::allows_implicit_invocation` implementation](https://github.com/openai/codex/blob/main/codex-rs/skills/src/model.rs#L31-L38)
  agree on the default.
- **[Documented from current source, not recommended as an enforced contract]**
  Codex's current `SkillPolicy` model also parses a `products` list, but the
  adjacent source comment says product gating still needs enforcement in skill
  selection/injection. [The current OpenAI source](https://github.com/openai/codex/blob/main/codex-rs/skills/src/model.rs#L72-L78)
  is therefore evidence of parsing, not a basis for a portability or enforcement
  guarantee.
- **[Unverified]** The reviewed OpenAI documentation and source-owned metadata
  reference do not state that Codex honors the top-level
  `disable-model-invocation` field. The reliable Codex contract for this purpose
  is the sidecar policy. [OpenAI's public field documentation](https://developers.openai.com/codex/skills#optional-metadata)
  is the authoritative affirmative contract reviewed here.

## 3. Claude Code: `disable-model-invocation`

- **[Documented]** Claude Code describes invocation control as a Claude Code
  extension to the Agent Skills standard. [Its skills overview](https://code.claude.com/docs/en/slash-commands#extend-claude-with-skills)
  explicitly separates the open standard from Claude Code invocation-control,
  subagent, and dynamic-context extensions.
- **[Documented]** By default, both the user and Claude can invoke a skill.
  `disable-model-invocation: true` changes that to user-only, leaves
  `/skill-name` available, and removes the skill description from model context.
  [Claude Code's control table](https://code.claude.com/docs/en/slash-commands#control-who-invokes-a-skill)
  states those effects; its [frontmatter reference](https://code.claude.com/docs/en/slash-commands#frontmatter-reference)
  states the default is `false`.
- **[Documented host enforcement]** If Claude attempts to invoke such a skill,
  Claude Code blocks the call and instructs Claude not to reproduce the protected
  steps another way. [The invocation-control section](https://code.claude.com/docs/en/slash-commands#control-who-invokes-a-skill)
  makes this stronger guarantee than simple catalog omission.
- **[Documented distinction]** `user-invocable: false` is the inverse control:
  the skill is hidden from the user command menu but remains model-invocable by
  default. [Claude Code's frontmatter reference](https://code.claude.com/docs/en/slash-commands#frontmatter-reference)
  documents the two independent switches.

## 4. GitHub Copilot: shared field, surface-specific confidence

### Copilot CLI

- **[Documented]** Copilot CLI loads project skills from `.github/skills`,
  `.agents/skills`, and `.claude/skills`, and injects a skill either through
  `/SKILL-NAME` or automatic agent invocation. [The CLI skills reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#skills-reference)
  documents both discovery and activation.
- **[Documented]** Its `SKILL.md` parser exposes `user-invocable` (default
  `true`) and `disable-model-invocation` (default `false`); the latter prevents
  automatic agent invocation. [The CLI frontmatter table](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#skill-frontmatter-fields)
  is the direct contract.
- **[Unverified]** The CLI reference does not list `agents/openai.yaml` as a
  metadata source. No affirmative first-party source was found for that sidecar
  in Copilot CLI. [The CLI's complete skills section](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#skills-reference)
  is the reviewed source.

### GitHub Copilot in VS Code

- **[Documented]** VS Code supports the same three project roots and the same
  two invocation-control fields. Its access table says the default is both slash
  and automatic access, `disable-model-invocation: true` is slash-only, and both
  flags together disable both paths. [VS Code's skill roots](https://code.visualstudio.com/docs/agent-customization/agent-skills#_create-a-skill),
  [field table](https://code.visualstudio.com/docs/agent-customization/agent-skills#_skill-file-format),
  and [access table](https://code.visualstudio.com/docs/agent-customization/agent-skills#_use-skills-as-slash-commands)
  document the behavior.
- **[Documented]** VS Code says Copilot discovers `name` and `description`, loads
  the full body after matching, and permits direct slash activation. [Its
  progressive-loading walkthrough](https://code.visualstudio.com/docs/agent-customization/agent-skills#_how-copilot-uses-skills)
  describes the three stages.
- **[Unverified]** The VS Code field and access tables do not state that the host
  reads `agents/openai.yaml`; no affirmative first-party source was found.
  [The VS Code Agent Skills page](https://code.visualstudio.com/docs/agent-customization/agent-skills)
  is the reviewed contract.

### Copilot cloud agent and code review

- **[Documented]** GitHub says Copilot decides to use skills from the prompt and
  description, and says code review can automatically use relevant skills.
  [The cloud-agent skills guide](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#how-copilot-uses-agent-skills)
  documents those statements.
- **[Unverified]** That guide's skill-file section lists the basic standard
  fields but does not separately document `disable-model-invocation`, an
  explicit slash path, or host blocking for cloud agent/code review. Treat the
  enforcement behavior as unestablished for those surfaces. [The same first-party
  guide](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#creating-and-adding-a-skill)
  is the basis for this bounded conclusion.

### Host behavior is not model choice

- **[Documented]** Copilot CLI exposes one host-level skills reference while
  separately allowing a user to choose Anthropic Claude, OpenAI GPT/Codex,
  Google Gemini, and other models. [The CLI's skills section](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#skills-reference)
  and [supported-model table](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#supported-models)
  document those independent controls.
- **[Documented]** VS Code describes models as generating text/tool requests that
  the agent loop interprets and executes; the model does not itself execute
  host tools. [VS Code's language-model concepts](https://code.visualstudio.com/docs/agents/concepts/language-models)
  documents that boundary.
- **[Inferred]** Therefore a Copilot session using an OpenAI model is still a
  Copilot host session: Copilot's documented `SKILL.md` parser and invocation
  controls apply, not Codex's `agents/openai.yaml` contract. Changing the model
  can change matching reliability or instruction-following quality, but it does
  not by itself change which host owns discovery and invocation policy. The
  [Copilot CLI host/model separation](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
  and [VS Code agent-loop boundary](https://code.visualstudio.com/docs/agents/concepts/language-models)
  support this inference.

## 5. Current Agentic Workflow repository artifacts

- **[Repository-observed]** The provider declaration maps Codex invocation to
  `agents/openai.yaml:policy.allow_implicit_invocation`, Copilot invocation to
  `SKILL.md:disable-model-invocation`, and currently marks Claude Code
  unavailable because the project has no `.claude/skills` projection. See the
  checked-in [`providers.json`](../skills/agentic-workflow/payload/agent-workflow/providers.json).
- **[Repository-observed]** Installed provider skills such as `implement`,
  `to-spec`, and `to-tickets` carry both user-only declarations:
  `disable-model-invocation: true` in `SKILL.md` and
  `allow_implicit_invocation: false` in `agents/openai.yaml`. These installed,
  provider-owned files live under `.agents/skills/<name>/`; they are not
  checked-in framework artifacts.
- **[Repository-observed]** The declared Wayfinder adapter intentionally flips
  both spellings to implicit (`disable-model-invocation: false` and
  `allow_implicit_invocation: true`) while replacing the recognized upstream
  body with the Agentic Workflow-owned runtime projection.
  See [`providers.py`](../skills/agentic-workflow/scripts/providers.py) and the
  installed provider files under `.agents/skills/wayfinder/`.
- **[Repository-observed]** Provider validation checks the Copilot policy from
  `SKILL.md` and the Codex policy from `agents/openai.yaml`. Installation stages
  whole skill directories, applies only a declared adapter, validates the staged
  result, and moves the directory into `.agents/skills`; same-named existing
  directories are not overwritten. See `validate_staged_skill`,
  `adapter_plan`, and `stage_and_project_missing` in
  [`providers.py`](../skills/agentic-workflow/scripts/providers.py).
- **[Inferred]** The present dual metadata is not redundant for the currently
  claimed Codex and Copilot surfaces. Removing either declaration would discard
  the documented user-only control for one host family. The repository's
  [provider declaration](../skills/agentic-workflow/payload/agent-workflow/providers.json)
  and the host contracts above support that conclusion.

## 6. Small manual live-host matrix

**[Not run]** No live Codex, Copilot, Claude Code, cloud-agent, or code-review
test was executed for this report. The following matrix is a proposed manual
check, not evidence of current behavior.

Use a disposable repository and a disposable copy of the installed
`implement` provider skill under `.agents/skills/implement/`. Keep its two
user-only declarations unchanged. Place the copy in the host's documented
project root (`.agents/skills/implement` for Codex/Copilot; mirror it to
`.claude/skills/implement` for Claude Code). Use a minimal inert fixture and
inspect the host's skill-activation/log/tool event before approving any file or
command mutation.

Use this strongly matching prompt without an explicit skill token:

> Implement the approved work from the supplied spec now. Follow the complete
> implementation workflow, run its verification, and report completion.

Then use the same prompt with the host's explicit prefix as the positive
control (`$implement` for Codex, `/implement` for Copilot and Claude Code).

| Case | Host / selected model | Non-explicit expected result | Explicit control expected result | What it isolates |
| --- | --- | --- | --- | --- |
| A | Codex CLI or IDE extension | `implement` is not implicitly activated | `$implement` activates it | `agents/openai.yaml` enforcement |
| B | Copilot in VS Code / an available OpenAI model | `implement` is not auto-loaded | `/implement` loads it | Copilot host behavior with an OpenAI model |
| C | Copilot in VS Code / an available Anthropic model | Same as B | Same as B | Model choice versus the same Copilot host policy |
| D | Claude Code | Host blocks model invocation and does not reproduce the skill steps | `/implement` loads it | Claude Code's documented host enforcement |

For each case, record host version, selected model, exact fixture commit, prompt,
activation evidence, and whether any mutation was requested. A pass requires
both the non-explicit negative and explicit positive control. If the host has no
observable activation event, replace only the disposable copy's body with a
harmless unique response marker while preserving its original frontmatter and
sidecar, and disclose that fixture modification.

**[Unverified / separate follow-up]** Copilot cloud agent and Copilot code review
need their own remote matrix because neither the CLI nor VS Code result proves
cloud enforcement. Test them only after choosing a safe, observable remote
fixture and a non-mutating activation signal.

## Recommendation

- Keep both provider declarations for now: `disable-model-invocation` in
  `SKILL.md` for the documented Claude/Copilot hosts and
  `policy.allow_implicit_invocation` in `agents/openai.yaml` for Codex.
- Treat `agents/openai.yaml` as Codex-specific unless a Copilot first-party
  source or live test establishes otherwise.
- Update any architecture text that treats Copilot's user-only policy as merely
  inferred: it is now documented for Copilot CLI and VS Code. Keep cloud agent
  and code review qualified as unverified.
- If Claude Code projection is added later, preserve the existing provider
  `SKILL.md` frontmatter rather than translating invocation policy again; its
  `disable-model-invocation` field already expresses the documented Claude Code
  user-only contract.
- Run the four-case disposable live matrix before widening a claimed support
  guarantee, and add separate cloud/code-review tests before claiming those
  surfaces enforce the same opt-out.
