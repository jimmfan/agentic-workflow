# Package tests

Run `python3 scripts/verify_package.py --tests` from the
`skills/agentic-workflow` package directory. The verifier first validates the
package and then uses temporary Git repositories and a local archive fixture to
exercise install, update, status, remove, conflicts, tampering, idempotency,
version/checksum drift, path independence, and the one-operation bootstrap.

Tests make no persistent repository change and remove their temporary
directories automatically.
