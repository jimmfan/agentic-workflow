# Package tests

Run `python3 scripts/verify_package.py --tests` from the
`skills/agentic-workflow` package directory. The verifier first validates the
package and then uses ordinary temporary project directories, a temporary Git
repository, and local archive fixtures to exercise install, update, status,
remove, conflicts, tampering, idempotency, version/checksum drift, path
independence, absence of the Git executable, POSIX and Windows mode semantics,
unsafe-root refusal, and the one-operation bootstrap.

Tests make no persistent repository change and remove their temporary
directories automatically.
