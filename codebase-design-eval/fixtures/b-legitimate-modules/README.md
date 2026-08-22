# Checkout planning fixture

The project deliberately uses these domain terms:

- **Approval Policy**: compliance-owned rules deciding whether a sale is
  permitted in a jurisdiction. Compliance owns its release cadence and audit
  explanation codes.
- **Stock Ledger**: inventory-owned rules for allocating scarce stock fairly.
  Inventory changes this algorithm independently from compliance policy.
- **Checkout Plan**: checkout-owned composition of an approval and an
  allocation into the customer-facing decision.

All three modules currently run in-process, but they have different owners,
change reasons, invariants, and domain meanings. They may be deployed together
indefinitely. The established terms appear in support runbooks and audit logs;
renaming them requires a demonstrated clarity or correctness benefit.
