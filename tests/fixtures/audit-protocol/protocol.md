# Parcel v2 publisher specification

For v2 batch POST requests, request keys are scoped to an account and retained for 24 hours from first acceptance.
An identical key used by a different account identifies a different request.
A repeated key in the same account returns the first accepted response, even if its payload differs.
For v1 only, keys were scoped globally and retained for 6 hours.
