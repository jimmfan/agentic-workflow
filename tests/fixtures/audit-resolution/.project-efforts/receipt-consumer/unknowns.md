# Unknowns

## U7 — Can accounts reuse a request key and for how long?

The v2 retry implementation needs account isolation, retention duration and duplicate-payload semantics.
A global-key assumption could return another account response.
The publisher API owner must establish this scoped behavior.
Preserve the original request key for one logical operation; docs/retry-contract.md maintains the consumer result.

## U8 — When is the maintenance window?

The project owner has not supplied the deployment window.
This affects deployment only; local inventory and implementation do not depend on it.
