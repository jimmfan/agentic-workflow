# Batch export probe

We need to know whether a Python producer feeding a slow consumer through a pipe can finish with exact record counts for a 50000-line export.
A local disposable subprocess experiment is sufficient; no external services or production pipeline changes are in scope.
