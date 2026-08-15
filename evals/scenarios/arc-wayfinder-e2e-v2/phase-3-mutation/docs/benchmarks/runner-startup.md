# Runner startup benchmark

Requirement: additional usable runner capacity <= 60 seconds.

## Cold capacity

- p50 = 49 sec
- p95 = 86 sec
- p99 = 103 sec

## With 2 warm nodes

- p50 = 18 sec
- p95 = 41 sec
- p99 = 54 sec

## Cold timing decomposition

- EC2/node availability = 55-75 sec
- pod scheduling = 5-8 sec
- runner registration = 7-12 sec

