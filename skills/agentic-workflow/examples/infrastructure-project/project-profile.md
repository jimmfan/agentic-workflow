# Project profile

## Purpose and success

This illustrative infrastructure repository provisions an EKS platform and an
Actions Runner Controller deployment. Success means reviewable plans, valid Helm
rendering, healthy control-plane integrations, and explicitly authorized changes.
It demonstrates extension boundaries; it is not a complete production profile.

## Technology and architecture

Terraform defines AWS and cluster resources. Helm values configure Kubernetes
controllers and ARC runner scale sets. Identity, network reachability, scheduling,
and GitHub registration form separate diagnostic layers.

## Important paths

- `terraform/`: infrastructure modules and environment roots.
- `helm/`: chart values and release configuration.
- `clusters/`: cluster-specific declarative configuration.
- `docs/runbooks/`: operational evidence and recovery procedures.
- `docs/specs/`: project-owned durable platform specifications.
- `ai-workflow/state/records/TKT-*.md`: local canonical implementation tickets;
  no native tracker is configured in this fixture.

## Terminology

- `ARC`: GitHub Actions Runner Controller.
- `scale set`: an autoscaled group of ephemeral runner pods.
- `environment root`: the Terraform working directory for one environment.

## Constraints and policy

Never store AWS, Kubernetes, or GitHub credentials in the repository. Plans may
read remote systems and lock shared state, so they require explicit approval.
Apply, cluster mutation, runner registration changes, and destructive remediation
always require explicit authorization and an exact target.

## Delivery workflow

Format and statically validate locally, obtain approval for remote planning,
review plan artifacts without committing sensitive data, then obtain a separate
explicit approval for deployment. Independently review meaningful changes for
specification fit, correctness, security, validation gaps, and unintended scope;
the parent task dispositions findings and fixture maintainers may accept a
recorded material limitation. Trivial low-risk edits need only a parent sanity
check. This fixture defines no deploy command.

## Commands

### `terraform-format-check`

- Purpose: Verify canonical Terraform formatting without rewriting files.
- Action: `terraform fmt -check -recursive`
- Kind: `command`
- Working directory: `terraform/`
- Prerequisites: The project-pinned Terraform version.
- Environment: None.
- Scope: `repository-local`
- Safety: `read-only`
- Approval required: `no`
- Timeout: 2 minutes.
- Success: Exit status 0 with no files listed as incorrectly formatted.
- Unavailable: Report formatting verification blocked; do not install or choose a
  Terraform version implicitly.
- Side effects and reversal: None.

### `render-runner-chart`

- Purpose: Render the configured runner chart locally for structural review.
- Action: `helm template runner-set ./helm/runner-set --values ./helm/runner-set/values.yaml`
- Kind: `command`
- Working directory: `.`
- Prerequisites: The project-pinned Helm version and vendored/local chart content.
- Environment: None.
- Scope: `repository-local`
- Safety: `read-only`
- Approval required: `no`
- Timeout: 2 minutes.
- Success: Exit status 0 and rendered manifests on standard output.
- Unavailable: Report rendering blocked; do not fetch a chart or contact a
  cluster as an implicit fallback.
- Side effects and reversal: None.

### `plan-environment`

- Purpose: Produce a reviewed preview for one explicitly named environment.
- Action: `terraform plan -out=review.tfplan`
- Kind: `command`
- Working directory: `terraform/environments/EXPLICIT_ENVIRONMENT/`
- Prerequisites: Initialized pinned providers, remote-state access, and an exact
  environment selected by the user.
- Environment: Approved AWS credential variables; never store their values here.
- Scope: `external`
- Safety: `externally-mutating`
- Approval required: `yes`
- Timeout: 20 minutes.
- Success: Exit status 0 and a saved plan whose target and changes were reviewed.
- Unavailable: Report remote planning blocked; local validation is not a
  substitute for a reviewed plan.
- Side effects and reversal: May lock remote state temporarily and creates local
  `review.tfplan`; Terraform releases the lock, and deleting the plan reverses the
  local artifact. Never commit the plan.

### `inspect-runner-resources`

- Purpose: Read current controller and runner resource status for diagnosis.
- Action: `kubectl get pods,autoscalingrunnersets,ephemeralrunners -n EXPLICIT_NAMESPACE`
- Kind: `command`
- Working directory: `.`
- Prerequisites: An explicitly selected cluster context and namespace.
- Environment: Approved kubeconfig credential source; never store its contents.
- Scope: `external`
- Safety: `read-only`
- Approval required: `yes`
- Timeout: 1 minute.
- Success: Exit status 0 and output naming only the intended context/namespace.
- Unavailable: Continue with already captured evidence and report live cluster
  inspection blocked; do not switch context automatically.
- Side effects and reversal: Reads an external system but should not alter it;
  no reversal is expected.

## Debugging model

Trace GitHub workflow queue -> ARC listener/controller -> Kubernetes scheduling ->
node capacity -> runner pod startup -> network/DNS -> GitHub authentication and
registration -> job execution. Gather evidence at each boundary and identify the
earliest divergence before changing infrastructure.

## Decision considerations

Consider blast radius, environment isolation, IAM least privilege, identity
method, network egress, scheduler capacity, controller/version compatibility,
rollback, cost, and evidence retention.

## Profile maintenance

- Owner: Illustrative platform maintainers.
- Last reviewed: 2026-08-12.
- Becomes stale when: Framework fixtures change or example commands/systems are
  revised.
- Conflict behavior: Treat this as a non-runnable fixture; a real EKS/ARC project
  must replace placeholders and verify every command, context, and policy.
