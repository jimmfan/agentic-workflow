# Example application configuration

`main.tf.json` is a Terraform JSON configuration containing the application's EC2 launch template.
`test_configuration.py` contains editable application checks; run `python -m unittest -v` locally.
Extend those checks for the requested configuration change.
`verify.py` is a fixed independent acceptance checker, not an application test to edit.
Run `python verify.py` after implementation.
The checks inspect local configuration and do not contact AWS or demonstrate runtime enforcement.

The release operator supplies deployment inputs, owns AWS operations and live tests, and returns evidence for review.
No AWS credentials or live cloud tools are available here.
The background rollout policy is in [the rollout guide](docs/rollout.md); the current request determines which work is delegated.
