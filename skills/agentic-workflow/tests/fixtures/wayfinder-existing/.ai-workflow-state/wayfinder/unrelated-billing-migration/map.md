# Billing migration

## Destination

Move invoice storage to the billing service without changing response
serialization.

## Notes

- This effort is unrelated to the response-serialization implementation.
- Preserve it without loading or reconciling it.
