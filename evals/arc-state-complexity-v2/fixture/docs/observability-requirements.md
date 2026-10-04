# W4 observability contract

The synthetic platform exports the failed-job count metric named `FailedRunnerJobs` in namespace `ARC/Runner`, with the sole dimension `ClusterName = var.cluster_name`.
The publisher already exists outside this repository and emits a value every minute, including zero when no jobs fail.
Create one `aws_cloudwatch_metric_alarm` named `arc-failed-runner-jobs` using Sum, period 60 seconds, threshold 1, comparison `GreaterThanOrEqualToThreshold`, evaluation periods 1, datapoints to alarm 1, unit Count, and missing-data treatment `notBreaching`.
Set alarm_actions to the single approved SNS destination when it arrives; leave OK and insufficient-data actions empty.
No SNS topic, metric publisher, or additional resources are authorized for W4.
The destination ARN has not arrived, so W4 remains blocked.
Do not invent it or let this independent blocker stop W1/W2.
These are complete synthetic requirements, not recommendations for a real deployment.
