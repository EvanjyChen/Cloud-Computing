#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.storage_stack import StorageStack
from stacks.api_stack import ApiStack
from stacks.driver_stack import DriverStack

app = cdk.App()

storage = StorageStack(app, "A3-StorageStack")

api = ApiStack(
    app,
    "A3-ApiStack",
    bucket=storage.bucket,
    table=storage.table,
    index_name=storage.index_name,
)

DriverStack(
    app,
    "A3-DriverStack",
    bucket=storage.bucket,
    api_url=api.api_url,
)

app.synth()
