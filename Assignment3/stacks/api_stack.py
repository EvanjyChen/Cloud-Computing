from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_dynamodb as ddb,
)
from constructs import Construct


class ApiStack(Stack):
    """Plotting lambda + REST API (GET /plot)."""

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
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "TABLE_NAME": table.table_name,
                "INDEX_NAME": index_name,
            },
            layers=[matplotlib_layer],
        )
        table.grant_read_data(self.plotting_fn)
        bucket.grant_put(self.plotting_fn)

        api = apigw.RestApi(
            self,
            "PlottingApi",
            rest_api_name="A3-PlottingApi",
            deploy_options=apigw.StageOptions(stage_name="prod"),
        )
        api.root.add_resource("plot").add_method(
            "GET", apigw.LambdaIntegration(self.plotting_fn)
        )

        self.api_url = api.url + "plot"
        CfnOutput(self, "PlotApiUrl", value=self.api_url)
