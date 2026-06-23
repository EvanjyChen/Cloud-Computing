from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_dynamodb as ddb,
)
from constructs import Construct


class StorageStack(Stack):
    """S3 bucket (TestBucket) + DynamoDB table (S3-object-size-history) + GSI."""

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

        # GSI lets plotting lambda query latest entries per bucket efficiently
        self.table.add_global_secondary_index(
            index_name="bucket-timestamp-index",
            partition_key=ddb.Attribute(name="bucket_name", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="timestamp", type=ddb.AttributeType.NUMBER),
            projection_type=ddb.ProjectionType.ALL,
        )
