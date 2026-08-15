# Retry Helper

Implement `retry_delay` in `src/retry.py`.

Requirements:

- `attempt` is zero-based.
- Delay starts at `base_seconds`.
- Each retry doubles the previous delay.
- Delay must never exceed `max_seconds`.
- Negative attempts are invalid and must raise `ValueError`.
- Do not modify the public function signature.
