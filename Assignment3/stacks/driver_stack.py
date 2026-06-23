from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as s3,
)
from constructs import Construct


class DriverStack(Stack):
    """Driver lambda (uploads test objects to S3, then calls the plotting API)."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        bucket: s3.Bucket,
        api_url: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.driver_fn = _lambda.Function(
            self,
            "DriverFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambdas/driver"),
            timeout=Duration.seconds(60),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "API_URL": api_url,
            },
        )
        bucket.grant_read_write(self.driver_fn)
