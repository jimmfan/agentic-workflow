# Retry behaviour notes

The immediate request is to summarize which statements below are verified and which are assumed.

- Verified from `client.py` line 42: the client retries three times.
- Assumed from a chat message: the server enforces a ten-second timeout.
- Verified from the deployed configuration: backoff is exponential.

This is a one-time summary for the current conversation; no later work depends on it.
