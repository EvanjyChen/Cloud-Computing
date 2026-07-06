# Assignment 3 — CDK deployment of Assignment 2

CDK Python project that deploys the three lambdas, the S3 bucket, the DynamoDB
table (with GSI), the S3 → size-tracking event wiring, and the REST API.

The plotting function renders its PNG with the Python standard library. No
large binary package or region-specific third-party Lambda layer is required.

## Stacks
- `A3-StorageStack` — S3 bucket, DynamoDB table (+ GSI), size-tracking
  lambda, and S3 notifications
- `A3-ApiStack` — REST API and plotting lambda
- `A3-DriverStack` — driver lambda

No resource names are hardcoded — CDK auto-generates them and stacks reference
each other through construct objects.

## One-shot deploy in AWS CloudShell

```bash
# 1. clone
git clone <your-repo-url> a3 && cd a3

# 2. install deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. bootstrap (only first time per account/region)
npx --yes aws-cdk@latest bootstrap

# 4. deploy everything
npx --yes aws-cdk@latest deploy --all --require-approval never
```

## Demo

1. Open the CloudFormation console → show the 3 stacks (and their creation timestamps).
2. Under each stack's **Resources** tab they collectively show:
   3 Lambda functions, 1 S3 bucket, 1 DynamoDB table, 1 REST API.
3. Open the Lambda console → pick `A3-LambdaStack-DriverFn...` → **Test** with
   any empty event `{}`. It uploads/overwrites/deletes objects, then calls the
   plotting API.
4. Open DynamoDB → table items show the history rows.
5. Open S3 → `plot.png` is in the bucket.

## Clean up before demo

```bash
npx --yes aws-cdk@latest destroy --all --force
```
