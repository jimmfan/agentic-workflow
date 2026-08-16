# Frozen scenario metadata

Dataset: `ArtificialAnalysis/ITBench-AA`

Revision: `76df38a82288f75ba9e41dc8c515033332497473`

The ground-truth entity below is controller-only. Evaluated agents received the
listed read-only evidence files plus the pinned application topology, never this
table or `ground_truth.yaml`.

| Scenario | Agent files | Bytes | Frozen ground-truth entity | Ground-truth mechanism | Principal observed propagation |
| --- | ---: | ---: | --- | --- | --- |
| 102 | 204 | 697,828,573 | `Namespace/otel-demo` | Namespace memory quota prevents replacement pod scheduling | ad pod absent → ad service unavailable → frontend/proxy errors |
| 34 | 77 | 885,727,092 | `Pod/valkey-cart-.*` (Service alias accepted) | Valkey password authentication enabled without matching cart configuration | cart storage failure → checkout/frontend/proxy errors and latency |
| 83 | 78 | 972,610,982 | `NetworkChaos/otel-demo-email-checkout-network-partition` | Partition blocks checkout-to-email traffic | email call timeout → checkout latency/errors → proxy failures |
| 17 | 80 | 1,112,009,785 | `NetworkChaos/.*product-catalog` | Chaos-injected product-catalog network delay | catalog latency/errors → checkout/recommendation/frontend failures |
| 24 | 207 | 700,738,618 | `Deployment/checkout` | `KAFKA_ADDR=kafka:9999` points at an unserved port | checkout Kafka failure/restart → checkout/frontend/proxy errors |
| 80 | 81 | 905,250,348 | `NetworkChaos/otel-demo-checkout-kafka-network-partition` | Partition blocks checkout-to-Kafka traffic | Kafka publishing failure → checkout latency/errors → proxy failures |

Scenario 17's frozen fault prose says `To Be Specified` and names a Service in
the `fault` stanza while its root group requires a `NetworkChaos`. The group is
the frozen native matcher target, but this inconsistency is a limitation when
interpreting absolute correctness.

