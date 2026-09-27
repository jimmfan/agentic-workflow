# Upload size limit planning

The immediate request is to recommend the next planning step for raising the upload size limit.

Evidence discovered during inspection:

- The accepted API specification states the maximum upload size is 10 MB.
- The deployed gateway configuration enforces a 25 MB maximum for the same endpoint.
- Client, gateway, and storage changes all depend on which limit is authoritative, and each source claims to be current.
