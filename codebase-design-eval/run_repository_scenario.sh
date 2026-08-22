#!/bin/zsh
set -euo pipefail

if (( $# != 1 )); then
  print -u2 'usage: run_repository_scenario.sh <repetition>'
  exit 2
fi

repetition="$1"
eval_root="${0:A:h}"
repo_root="${eval_root:h}"

for condition in direct vanilla guarded; do
  common_text="$(<"$eval_root/prompts/common.md")"
  condition_text="$(<"$eval_root/prompts/$condition.md")"
  scenario_text="$(<"$eval_root/prompts/scenario-d.md")"
  prompt="$common_text

$condition_text

$scenario_text"
  output_root="$eval_root/runs/$condition"
  output_path="$output_root/scenario-d-r${repetition}.md"
  event_path="/tmp/codebase-design-${condition}-d-r${repetition}.jsonl"
  mkdir -p "$output_root"

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
    --cd "$repo_root" \
    --output-last-message "$output_path" \
    "$prompt" > "$event_path"

  python3 "$eval_root/record_run.py" \
    --output "$output_path" \
    --events "$event_path" \
    --workspace "$repo_root" \
    --condition "$condition" \
    --scenario d \
    --repetition "$repetition" \
    --elapsed-seconds "$((SECONDS - run_started))" \
    --run-kind controlled_live_repository
done
