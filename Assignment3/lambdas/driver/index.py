"""Driver lambda: create/update/delete objects in S3, then call the plotting API."""
import os
import time
import urllib.request

import boto3

BUCKET_NAME = os.environ["BUCKET_NAME"]
API_URL = os.environ.get("API_URL", "")

s3 = boto3.client("s3")


def lambda_handler(event, context):
    # 1) create assignment1.txt with body "Empty Assignment 1"
    s3.put_object(Bucket=BUCKET_NAME, Key="assignment1.txt", Body=b"Empty Assignment 1")
    time.sleep(2)

    # 2) overwrite with "Empty Assignment 2222222222"
    s3.put_object(Bucket=BUCKET_NAME, Key="assignment1.txt", Body=b"Empty Assignment 2222222222")
    time.sleep(2)

    # 3) delete assignment1.txt
    s3.delete_object(Bucket=BUCKET_NAME, Key="assignment1.txt")
    time.sleep(2)

    # 4) create assignment2.txt with body "33"
    s3.put_object(Bucket=BUCKET_NAME, Key="assignment2.txt", Body=b"33")
    time.sleep(2)

    # 5) call the plotting REST API
    api_response = ""
    if API_URL:
        with urllib.request.urlopen(API_URL, timeout=30) as resp:
            api_response = resp.read().decode("utf-8")
            print("Plot API response:", api_response)

    return {"status": "ok", "api_url": API_URL, "api_response": api_response}
