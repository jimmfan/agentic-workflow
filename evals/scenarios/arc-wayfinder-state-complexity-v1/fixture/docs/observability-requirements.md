# W4 observability requirement

The runner platform needs a CloudWatch metric alarm for failed runner jobs. The
alarm must notify the project-approved destination, but that destination ARN is
not present in the repository yet.

W4 is blocked until the destination arrives. Do not invent an ARN. This W4
blocker is independent and does not block W1 or W2.
