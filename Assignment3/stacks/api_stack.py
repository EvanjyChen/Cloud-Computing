from aws_cdk import (
    Stack,
    CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct


class ApiStack(Stack):
    """REST API → plotting lambda (GET /plot)."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        plotting_fn: _lambda.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = apigw.RestApi(
            self,
            "PlottingApi",
            rest_api_name="A3-PlottingApi",
            deploy_options=apigw.StageOptions(stage_name="prod"),
        )

        plot_resource = api.root.add_resource("plot")
        plot_resource.add_method("GET", apigw.LambdaIntegration(plotting_fn))

        self.api_url = api.url + "plot"

        CfnOutput(self, "PlotApiUrl", value=self.api_url)
