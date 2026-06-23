from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_dynamodb as ddb,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n,
)
from constructs import Construct


class StorageStack(Stack):
    """S3 bucket + DynamoDB table (+GSI) + size-tracking lambda + S3 event wiring.

    Size-tracking lambda lives here because S3 notifications mutate the bucket
    resource itself; keeping the lambda in a separate stack creates a cyclic
    cross-stack reference.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "TestBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        self.table = ddb.Table(
            self,
            "SizeHistoryTable",
            partition_key=ddb.Attribute(name="bucket_name", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="timestamp", type=ddb.AttributeType.NUMBER),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.index_name = "bucket-timestamp-index"
        self.table.add_global_secondary_index(
            index_name=self.index_name,
            partition_key=ddb.Attribute(name="bucket_name", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="timestamp", type=ddb.AttributeType.NUMBER),
            projection_type=ddb.ProjectionType.ALL,
        )

        self.size_tracking_fn = _lambda.Function(
            self,
            "SizeTrackingFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambdas/size_tracking"),
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": self.bucket.bucket_name,
                "TABLE_NAME": self.table.table_name,
            },
        )
        self.bucket.grant_read(self.size_tracking_fn)
        self.table.grant_write_data(self.size_tracking_fn)

        notification = s3n.LambdaDestination(self.size_tracking_fn)
        self.bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
        self.bucket.add_event_notification(s3.EventType.OBJECT_REMOVED, notification)
