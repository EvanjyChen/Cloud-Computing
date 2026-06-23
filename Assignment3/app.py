#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.storage_stack import StorageStack
from stacks.lambda_stack import LambdaStack
from stacks.api_stack import ApiStack
from stacks.event_stack import EventStack

app = cdk.App()

storage = StorageStack(app, "A3-StorageStack")

lambdas = LambdaStack(
    app,
    "A3-LambdaStack",
    bucket=storage.bucket,
    table=storage.table,
)

api = ApiStack(
    app,
    "A3-ApiStack",
    plotting_fn=lambdas.plotting_fn,
)

# driver lambda needs the API URL, set it after api stack is built
lambdas.driver_fn.add_environment("API_URL", api.api_url)

EventStack(
    app,
    "A3-EventStack",
    bucket=storage.bucket,
    size_tracking_fn=lambdas.size_tracking_fn,
)

app.synth()
