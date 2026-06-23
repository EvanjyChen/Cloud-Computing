"""Plotting lambda: read DDB history -> plot size over last 10s + max over past -> upload PNG to S3."""
import io
import os
import time
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]
INDEX_NAME = os.environ["INDEX_NAME"]

s3 = boto3.client("s3")
ddb = boto3.resource("dynamodb")
table = ddb.Table(TABLE_NAME)

PLOT_KEY = "plot.png"


def _to_float(x):
    return float(x) if isinstance(x, Decimal) else x


def query_last_10_seconds(bucket_name, now_ms):
    start = now_ms - 10_000
    resp = table.query(
        IndexName=INDEX_NAME,
        KeyConditionExpression=Key("bucket_name").eq(bucket_name)
        & Key("timestamp").between(start, now_ms),
    )
    return resp.get("Items", [])


def query_historical_max(bucket_name):
    resp = table.query(
        IndexName=INDEX_NAME,
        KeyConditionExpression=Key("bucket_name").eq(bucket_name),
    )
    items = resp.get("Items", [])
    if not items:
        return 0
    return max(_to_float(i["size_bytes"]) for i in items)


def lambda_handler(event, context):
    now_ms = int(time.time() * 1000)

    recent = query_last_10_seconds(BUCKET_NAME, now_ms)
    recent.sort(key=lambda i: _to_float(i["timestamp"]))

    times = [_to_float(i["timestamp"]) / 1000.0 for i in recent]
    sizes = [_to_float(i["size_bytes"]) for i in recent]
    hist_max = query_historical_max(BUCKET_NAME)

    fig, ax = plt.subplots(figsize=(8, 4))
    if times:
        t0 = times[0]
        ax.plot([t - t0 for t in times], sizes, marker="o", label="size (last 10s)")
    ax.axhline(hist_max, color="red", linestyle="--", label=f"historical max = {hist_max:.0f}")
    ax.set_xlabel("seconds since first sample")
    ax.set_ylabel("bucket size (bytes)")
    ax.set_title(f"Bucket {BUCKET_NAME}")
    ax.legend()
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=PLOT_KEY,
        Body=buf.getvalue(),
        ContentType="image/png",
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": f'{{"plot_s3_key": "{PLOT_KEY}", "historical_max": {hist_max}, "samples": {len(times)}}}',
    }
