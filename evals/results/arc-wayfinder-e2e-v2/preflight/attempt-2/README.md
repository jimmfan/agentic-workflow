# Isolation audit attempt 2

This network-enabled preflight completed all three fresh probes and passed the
static, canary, execution-ID, installation-integrity, and cleanup checks.

Manual inspection rejected the machine conclusion before any evaluated phase
started. Condition A returned `controller_conversation_visible: true`; the
grader's regular expression did not recognize the underscored JSON key. The
answer did not expose any controller content, and all parent/sibling canaries
remained absent, so the boolean was ambiguous rather than evidence of actual
crossover. Nevertheless, accepting it would make the isolation claim stronger
than the raw evidence supports.

The associated evaluator freeze is retained here. The next evaluator revision
replaces that ambiguous boolean with
`controller_conversation_excerpt`: the probe must provide exact inherited
content or `null`, and the grader parses the JSON value directly.
