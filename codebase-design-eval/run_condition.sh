#!/bin/zsh
set -euo pipefail

if (( $# < 2 )); then
  print -u2 'usage: run_condition.sh <condition> <repetition> [scenario ...]'
  exit 2
fi

condition="$1"
repetition="$2"
eval_root="${0:A:h}"
repo_root="${eval_root:h}"
condition_prompt="$eval_root/prompts/$condition.md"
output_root="$eval_root/runs/$condition"
scenarios=("${@:3}")

if (( ${#scenarios} == 0 )); then
  scenarios=(a b c)
fi

if [[ ! -f "$condition_prompt" ]]; then
  print -u2 "missing condition prompt: $condition_prompt"
  exit 2
fi

mkdir -p "$output_root"

for scenario in "${scenarios[@]}"; do
  if [[ "$scenario" != [abc] ]]; then
    print -u2 "unsupported hosted scenario: $scenario"
    exit 2
  fi
  common_text="$(<"$eval_root/prompts/common.md")"
  condition_text="$(<"$condition_prompt")"
  scenario_text="$(<"$eval_root/prompts/scenario-$scenario.md")"
  prompt="$common_text

$condition_text

$scenario_text"
  output_path="$output_root/scenario-${scenario}-r${repetition}.md"
  event_path="/tmp/codebase-design-${condition}-${scenario}-r${repetition}.jsonl"
  run_workspace="$(mktemp -d "/tmp/codebase-design-${condition}-${scenario}-r${repetition}.XXXXXX")"
  trap 'rm -rf "$run_workspace"' EXIT

  case "$scenario" in
    a) fixture_name='a-overengineered' ;;
    b) fixture_name='b-legitimate-modules' ;;
    c) fixture_name='c-testing-trap' ;;
  esac
  mkdir -p "$run_workspace/codebase-design-eval/fixtures"
  cp -R "$eval_root/fixtures/$fixture_name" "$run_workspace/codebase-design-eval/fixtures/"

  if [[ "$condition" == "vanilla" ]]; then
    mkdir -p "$run_workspace/.agents/skills/codebase-design"
    cp \
      "$repo_root/.agents/skills/codebase-design/SKILL.md" \
      "$repo_root/.agents/skills/codebase-design/DEEPENING.md" \
      "$repo_root/.agents/skills/codebase-design/DESIGN-IT-TWICE.md" \
      "$run_workspace/.agents/skills/codebase-design/"
  elif [[ "$condition" == "guarded" ]]; then
    mkdir -p "$run_workspace/codebase-design-eval/candidate-codebase-design"
    cp \
      "$eval_root/candidate-codebase-design/SKILL.md" \
      "$eval_root/candidate-codebase-design/DEEPENING.md" \
      "$eval_root/candidate-codebase-design/DESIGN-IT-TWICE.md" \
      "$run_workspace/codebase-design-eval/candidate-codebase-design/"
  fi

  run_started=$SECONDS
  codex exec \
    --ephemeral \
    --ignore-user-config \
    --ignore-rules \
    --json \
    --color never \
    --sandbox read-only \
    --model gpt-5.4 \
    --config 'model_reasoning_effort="high"' \
    --skip-git-repo-check \
    --cd "$run_workspace" \
    --output-last-message "$output_path" \
    "$prompt" > "$event_path"

  python3 "$eval_root/record_run.py" \
    --output "$output_path" \
    --events "$event_path" \
    --workspace "$run_workspace" \
    --condition "$condition" \
    --scenario "$scenario" \
    --repetition "$repetition" \
    --elapsed-seconds "$((SECONDS - run_started))"

  rm -rf "$run_workspace"
  trap - EXIT
done
