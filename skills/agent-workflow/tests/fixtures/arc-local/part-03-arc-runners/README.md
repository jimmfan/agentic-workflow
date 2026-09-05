# Part 03: Local ARC runners

`values.yaml` sets `runnerScaleSetName: arc-runner-set`.
Local workflow jobs target this scale set with `runs-on: arc-runner-set`.
The namespace remains `arc-runners`.

Run `python part-03-arc-runners/verify.py` from the repository root to check that the local values and documented job target agree.
This is an offline configuration check; it does not deploy runners or prove cluster health.
