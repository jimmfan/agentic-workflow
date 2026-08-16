# Blinded entity and condition adjudication packet

Status: post-run packet; the frozen native scores have not been changed

Purpose: resolve entity-layer ambiguities and the native metric's omission of
condition correctness. Opaque IDs deliberately hide condition and repetition.
An adjudicator should review snapshot evidence and causal conditions without
learning A/B/C. This packet must produce a separate sensitivity result, never a
replacement presented as the preregistered native score.

## Questions

For each family, decide independently:

1. Does a controller (`Schedule`) count as the causal entity when it repeatedly
   creates the ground-truth `NetworkChaos`?
2. Does a generated child `NetworkChaos` whose name adds a random suffix count
   as the ground-truth base-name entity?
3. Does the concrete `ResourceQuota` count when ground truth names its containing
   `Namespace` but attributes the same quota mechanism?
4. Does a `Deployment` count when ground truth accepts a Pod and Service alias,
   and is an entity match valid when the submitted fault condition is wrong?

## Scenario 102: quota entity layer

Ground-truth target: `Namespace/-/otel-demo`, memory quota enforcement.

Eight submissions name only `ResourceQuota/otel-demo/otel-demo-memory`; one also
adds `Deployment/otel-demo/ad`. Every condition describes the quota rejecting
the ad replacement pod.

Opaque IDs: `2f9045880856`, `abe198d8a6dd`, `4e92f4285804`, `225ee2d986d6`,
`78adbacf7c91`, `94cb5d22c49c`, `e39284053400`, `2c517ebaf3f7`, `727d6371268b`.

## Scenario 17: Schedule and generated child layer

Ground-truth target: `NetworkChaos/chaos-mesh/.*product-catalog`.

Eight submissions name `Schedule/chaos-mesh/otel-demo-product-catalog-network-delay`;
one names the generated `PodNetworkChaos` for the product-catalog pod. All
conditions describe recurring chaos-injected network delay and downstream
timeouts. One Schedule submission uses namespace `otel-demo` instead of
`chaos-mesh`.

Opaque IDs: `2efc7287da8b`, `95b1cb693155`, `90f1f6d7c300`, `db06e1792017`,
`14c854f51987`, `3e789ff9a50b`, `64aeba63ecff`, `84bad547f1f8`, `91a8580ec4f9`.

## Scenario 34: entity match versus wrong mechanism

Ground-truth target: `Pod/otel-demo/valkey-cart-.*`, with the Valkey Service as
an accepted alias. The mechanism is password authentication enabled without a
matching cart configuration.

One submission names the exact Valkey Pod but describes it only as nonresponsive;
the other eight name a Deployment (`valkey-cart` seven times and `cart` once).
The Deployment submissions attribute the failure to CPU starvation. No
submission identifies the password-authentication mismatch.

Opaque IDs: `dffd60a17313`, `1be708c58c34`, `181e363ba97f`, `9a0aed8b634a`,
`b573f24b251b`, `84266072e82d`, `e09c82544e55`, `94392dcb91cb`, `9beb37edba0e`.

The strict native grader awards the exact-Pod submission despite the missing
ground-truth mechanism. This is a condition-validity audit, not merely an alias
question.

## Scenario 83: Schedule and generated NetworkChaos names

Ground-truth target:
`NetworkChaos/chaos-mesh/otel-demo-email-checkout-network-partition`.

Five submissions name the parent `Schedule`; four name generated `NetworkChaos`
children with suffixes such as `-5c2dr`, `-7rvkf`, or `-drrh9`. All conditions
describe the checkout/email partition and its timeout propagation.

Opaque IDs: `f53f8a696dfc`, `2e8a824d26d5`, `f887229b02ca`, `7f66d83b0d22`,
`7f579b5caf03`, `f84524045a0e`, `0780e467ea04`, `caa2ca2187e1`, `4d3bfb7b7cc3`.

## Scenario 80: Schedule and generated NetworkChaos names

Ground-truth target:
`NetworkChaos/chaos-mesh/otel-demo-checkout-kafka-network-partition`.

Six submissions name the parent `Schedule`; three name generated `NetworkChaos`
children with suffixes such as `-wrbzf` or `-dtxwx`. All conditions describe
the checkout/Kafka partition and its downstream failures.

Opaque IDs: `d4fdd574338f`, `c9caf63f380e`, `a28851d4fe2a`, `716807c26038`,
`de07c12fb58a`, `500273f9e94b`, `f54115fa801d`, `4ca86cb49fc8`, `fba0df904ae7`.

## Scenario 24

No adjudication is needed. All nine submissions exactly name
`Deployment/otel-demo/checkout` and identify the bad Kafka port.

