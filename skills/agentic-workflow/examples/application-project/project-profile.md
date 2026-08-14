# Project profile

## Purpose and success

This illustrative application serves a versioned JSON API for internal clients.
Success means compatible responses, validated persistence, and passing local
quality checks. This is a profile fixture, not a runnable application.

## Technology and architecture

Python request handlers call a service layer, which owns business rules and uses
a PostgreSQL repository adapter. Schema migrations are applied separately from
application startup.

## Important paths

- `src/api/`: transport and validation.
- `src/service/`: business behavior.
- `src/storage/`: persistence adapters.
- `tests/`: unit and integration tests.
- `migrations/`: reviewed schema changes.
- `docs/specs/`: project-owned durable behavior specifications.
- `docs/tickets/`: project-owned local implementation tickets; no native tracker
  is configured in this fixture.

## Terminology

- `repository`: the application's persistence adapter, not the Git repository.
- `compatibility`: existing documented response fields retain their meaning.

## Constraints and policy

Do not log access tokens or customer payloads. Database migrations need reviewer
approval and a rollback description. Preserve API compatibility unless the change
is explicitly versioned.

## Delivery workflow

Plan meaningful behavior changes, implement locally, run formatting and tests,
then independently review meaningful changes for specification fit, correctness,
security, validation gaps, and unintended scope before opening a reviewed change.
The parent task dispositions findings; fixture maintainers may accept a recorded
material limitation. Trivial low-risk edits need only a parent sanity check.
Deployment is intentionally not configured here.

## Commands

### `lint-python`

- Purpose: Detect Python correctness and style problems without changing files.
- Action: `python -m ruff check --no-cache .`
- Kind: `command`
- Working directory: `.`
- Prerequisites: Project development dependencies installed.
- Environment: None.
- Scope: `repository-local`
- Safety: `read-only`
- Approval required: `no`
- Timeout: 2 minutes.
- Success: Exit status 0 with no diagnostics.
- Unavailable: Report blocked; do not substitute another linter.
- Side effects and reversal: None; cache is disabled.

### `test-application`

- Purpose: Exercise application behavior and persistence boundaries locally.
- Action: `python -m pytest`
- Kind: `command`
- Working directory: `.`
- Prerequisites: Project development dependencies and the documented local test
  database fixture.
- Environment: `TEST_DATABASE_URL` may be required; never store its value here.
- Scope: `host-local`
- Safety: `locally-mutating`
- Approval required: `no`
- Timeout: 10 minutes.
- Success: Exit status 0 and all collected tests pass.
- Unavailable: Run only unaffected unit-test paths if known and report the
  integration coverage as blocked; do not claim full verification.
- Side effects and reversal: May create `.pytest_cache/` and local test rows;
  delete the cache and reset the disposable test database to reverse.

## Debugging model

Trace client request -> routing/validation -> service rule -> repository adapter
-> database. Compare the earliest divergent layer with a known-good request, and
separate application errors from dependency or data failures.

## Decision considerations

Consider API compatibility, transaction boundaries, migration rollback, data
classification, and operational observability before choosing an implementation.

## Profile maintenance

- Owner: Illustrative application maintainers.
- Last reviewed: 2026-08-12.
- Becomes stale when: Framework fixtures change or the example architecture is
  revised.
- Conflict behavior: Treat this as a non-runnable fixture; update it alongside
  contract changes and never infer commands for a real project from it.
