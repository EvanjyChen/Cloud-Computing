"""Size-tracking lambda: S3 event -> compute bucket size -> write DDB row."""
import os
import time
import boto3

TABLE_NAME = os.environ["TABLE_NAME"]

s3 = boto3.client("s3")
ddb = boto3.resource("dynamodb")
table = ddb.Table(TABLE_NAME)


def compute_bucket_size(bucket_name):
    total_size = 0
    total_count = 0
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            total_size += obj["Size"]
            total_count += 1
    return total_size, total_count


def lambda_handler(event, context):
    bucket_names = {r["s3"]["bucket"]["name"] for r in event.get("Records", [])}
    if not bucket_names:
        return {"status": "no records"}

    for bucket_name in bucket_names:
        size_bytes, object_count = compute_bucket_size(bucket_name)
        timestamp = int(time.time() * 1000)
        table.put_item(
            Item={
                "bucket_name": bucket_name,
                "timestamp": timestamp,
                "size_bytes": size_bytes,
                "object_count": object_count,
            }
        )
        print(f"{bucket_name}: size={size_bytes} count={object_count} ts={timestamp}")

    return {"status": "ok", "buckets": list(bucket_names)}
