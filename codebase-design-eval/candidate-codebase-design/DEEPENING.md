# Deepening

How to deepen a cluster of shallow modules safely, given its dependencies. Assumes the vocabulary in [SKILL.md](SKILL.md) — **module**, **interface**, **seam**, **adapter**.

Before deepening, establish concrete caller complexity, duplicated knowledge,
scattered change, or navigation cost. Technical mergeability is not sufficient;
preserve modules that earn their keep through cohesion, ownership, domain
semantics, independent evolution, trust, lifecycle, deployment, or failure
isolation.

## Dependency categories

When assessing a candidate for deepening, classify its dependencies. The category informs how the deepened module is tested across its seam; it does not by itself decide whether modules should merge.

### 1. In-process

Pure computation, in-memory state, no I/O. Technically easy to deepen. Merge when the separation is pass-through and no demonstrated architectural seam earns its keep; otherwise preserve the seam and improve only incidental mechanics. No adapter is needed solely for testability.

### 2. Local-substitutable

Dependencies that have sufficiently faithful local test stand-ins (PGLite for Postgres, in-memory filesystem). Deepenable when the stand-in exists and fidelity is adequate. The deepened module can be tested with the stand-in running in the test suite. A stand-in does not erase a real ownership, contract, trust, or failure seam.

### 3. Remote but owned (Ports & Adapters)

Your own services across a network boundary (microservices, internal APIs). Define a **port** (interface) at the seam. The deep module owns the logic; the transport is injected as an **adapter**. Tests use an in-memory adapter. Production uses an HTTP/gRPC/queue adapter.

Recommendation shape: *"Define a port at the seam, implement an HTTP adapter for production and an in-memory adapter for testing, so the logic sits in one deep module even though it's deployed across a network."*

### 4. True external (Mock)

Third-party services (Stripe, Twilio, etc.) you don't control. The deepened module takes the external dependency as an injected port; tests provide a mock adapter.

## Seam discipline

- **Adapter count is a justification prompt.** Do not add a port for vague future variation. Preserve seams justified by actual variation or an external contract, ownership, trust, lifecycle, deployment, or failure boundary even when only one production adapter exists.
- **Internal seams vs external seams.** A deep module can have internal seams (private to its implementation, used by its own tests) as well as the external seam at its interface. Don't expose internal seams through the interface just because tests use them.

## Testing strategy: replace redundancy, don't delete evidence

- Write new tests at the deepened module's interface.
- Delete an old lower-level test only after showing that equivalent behavior and failure coverage exists at an equally clear, reliable, and maintainable surface.
- Preserve focused tests that cheaply protect algorithms, invariants, parsing, concurrency, security, failure behavior, protocol edge cases, or diagnostics that would be obscured at a higher level.
- Tests assert on observable outcomes through the interface, not incidental internal state.
- Tests should survive internal refactors when they describe the same behavior. A lower-level public behavior or concentrated hazard is not incidental merely because a higher-level interface also exists.
