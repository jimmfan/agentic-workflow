# Settlement reconciliation requirements

Reconciliation must safely process settlement records from the payment
provider. Local fixtures cover unique settlement IDs only. The repository has
no provider contract, captured duplicate response, or sandbox observation that
establishes whether duplicate settlement IDs are idempotent, rejected, or
represent corrected records.

Work that does not depend on duplicate semantics may continue, including
inventorying current call sites and preparing a read-only fixture set.
