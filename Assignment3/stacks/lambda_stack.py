from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as ddb,
)
from constructs import Construct


class LambdaStack(Stack):
    """Plotting lambda + driver lambda (size-tracking lives in StorageStack)."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        bucket: s3.Bucket,
        table: ddb.Table,
        index_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        common_env = {
            "BUCKET_NAME": bucket.bucket_name,
            "TABLE_NAME": table.table_name,
        }

        matplotlib_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "AWSSDKPandasLayer",
            f"arn:aws:lambda:{self.region}:336392948345:layer:AWSSDKPandas-Python311:13",
        )

        self.plotting_fn = _lambda.Function(
            self,
            "PlottingFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambdas/plotting"),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={**common_env, "INDEX_NAME": index_name},
            layers=[matplotlib_layer],
        )
        table.grant_read_data(self.plotting_fn)
        bucket.grant_put(self.plotting_fn)

        self.driver_fn = _lambda.Function(
            self,
            "DriverFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambdas/driver"),
            timeout=Duration.seconds(60),
            environment=common_env,  # API_URL injected later in app.py
        )
        bucket.grant_read_write(self.driver_fn)
