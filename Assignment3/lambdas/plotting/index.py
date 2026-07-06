"""Read DDB history, render a dependency-free PNG chart, and upload it to S3."""
import json
import os
import struct
import time
import zlib
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

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


def _png_chunk(chunk_type, data):
    payload = chunk_type + data
    return (
        struct.pack(">I", len(data))
        + payload
        + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
    )


def render_plot(times, sizes, historical_max):
    """Render an 800x400 RGB line chart using only the standard library."""
    width, height = 800, 400
    left, right, top, bottom = 60, 30, 30, 50
    chart_width = width - left - right
    chart_height = height - top - bottom
    pixels = bytearray([255]) * (width * height * 3)

    def set_pixel(x, y, color):
        if 0 <= x < width and 0 <= y < height:
            offset = (y * width + x) * 3
            pixels[offset : offset + 3] = bytes(color)

    def draw_line(x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        error = dx + dy
        while True:
            set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            twice_error = 2 * error
            if twice_error >= dy:
                error += dy
                x0 += sx
            if twice_error <= dx:
                error += dx
                y0 += sy

    axis_color = (35, 35, 35)
    grid_color = (220, 220, 220)
    data_color = (30, 100, 210)
    max_color = (210, 45, 45)

    for step in range(5):
        y = top + round(step * chart_height / 4)
        draw_line(left, y, width - right, y, grid_color)
    draw_line(left, top, left, height - bottom, axis_color)
    draw_line(left, height - bottom, width - right, height - bottom, axis_color)

    y_max = max([1.0, float(historical_max), *[float(v) for v in sizes]])

    def scale_y(value):
        return height - bottom - round(float(value) / y_max * chart_height)

    max_y = scale_y(historical_max)
    for x in range(left, width - right + 1, 12):
        draw_line(x, max_y, min(x + 6, width - right), max_y, max_color)

    if times:
        first_time = min(times)
        time_span = max(max(times) - first_time, 1.0)
        points = [
            (
                left + round((timestamp - first_time) / time_span * chart_width),
                scale_y(size),
            )
            for timestamp, size in zip(times, sizes)
        ]
        for start, end in zip(points, points[1:]):
            draw_line(*start, *end, data_color)
        for x, y in points:
            for delta in range(-3, 4):
                set_pixel(x + delta, y, data_color)
                set_pixel(x, y + delta, data_color)

    scanlines = b"".join(
        b"\x00" + bytes(pixels[y * width * 3 : (y + 1) * width * 3])
        for y in range(height)
    )
    signature = b"\x89PNG\r\n\x1a\n"
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        signature
        + _png_chunk(b"IHDR", header)
        + _png_chunk(b"IDAT", zlib.compress(scanlines, level=9))
        + _png_chunk(b"IEND", b"")
    )


def lambda_handler(event, context):
    now_ms = int(time.time() * 1000)

    recent = query_last_10_seconds(BUCKET_NAME, now_ms)
    recent.sort(key=lambda i: _to_float(i["timestamp"]))

    times = [_to_float(i["timestamp"]) / 1000.0 for i in recent]
    sizes = [_to_float(i["size_bytes"]) for i in recent]
    hist_max = query_historical_max(BUCKET_NAME)

    plot_png = render_plot(times, sizes, hist_max)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=PLOT_KEY,
        Body=plot_png,
        ContentType="image/png",
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "plot_s3_key": PLOT_KEY,
                "historical_max": hist_max,
                "samples": len(times),
            }
        ),
    }
