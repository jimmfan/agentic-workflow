# Imported Platform Facts

This file represents information imported from an external platform system. It is evidence available for the current work session, not a durable architecture decision, and it may disappear later.

Verified current platform fact:

- Approved runner AMI SSM parameter:
  `/platform/eks/runner/ami/latest`

This parameter is maintained by the platform image pipeline and should be referenced rather than replacing it with a hard-coded AMI ID.

No approved EC2 instance family is available from this source.

No approved runner/node isolation decision is available from this source.
