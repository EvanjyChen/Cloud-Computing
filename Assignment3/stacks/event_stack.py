from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n,
)
from constructs import Construct


class EventStack(Stack):
    """Wire S3 ObjectCreated / ObjectRemoved events to the size-tracking lambda."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        bucket: s3.Bucket,
        size_tracking_fn: _lambda.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        notification = s3n.LambdaDestination(size_tracking_fn)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
        bucket.add_event_notification(s3.EventType.OBJECT_REMOVED, notification)
