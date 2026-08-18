from pathlib import Path


effort = Path(".agent-workflow-state/wayfinder/deployment-mode")
evidence = sorted((effort / "evidence").glob("E2-*.md"))
unknowns = sorted((effort / "unknowns").glob("U1-*.md"))
fact = (effort / "facts/F1-deployment-mode-is-dedicated.md").read_text()
decision = (effort / "decisions/D1-use-dedicated-capacity-policy.md").read_text()
mapping = (effort / "map.md").read_text()

checks = [
    len(evidence) == 1
    and "deployment_mode=shared" in evidence[0].read_text()
    and "Source: config.txt" in evidence[0].read_text()
    and "Scope: current deployment configuration" in evidence[0].read_text()
    and "## Limitations" in evidence[0].read_text(),
    len(unknowns) == 1
    and "deployment mode" in unknowns[0].read_text().lower()
    and "- Status: open" in unknowns[0].read_text(),
    "- Status: disputed" in fact and "- Contradicted by: E2" in fact,
    "F1 is disputed" in mapping,
    "review D1" in mapping,
    "Use the dedicated capacity policy unless its authority supersedes this decision." in decision,
    not (effort / "tickets").exists(),
]

raise SystemExit(0 if all(checks) else 1)
