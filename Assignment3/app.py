#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.storage_stack import StorageStack
from stacks.lambda_stack import LambdaStack
from stacks.api_stack import ApiStack

app = cdk.App()

storage = StorageStack(app, "A3-StorageStack")

lambdas = LambdaStack(
    app,
    "A3-LambdaStack",
    bucket=storage.bucket,
    table=storage.table,
    index_name=storage.index_name,
)

api = ApiStack(app, "A3-ApiStack", plotting_fn=lambdas.plotting_fn)

lambdas.driver_fn.add_environment("API_URL", api.api_url)

app.synth()
