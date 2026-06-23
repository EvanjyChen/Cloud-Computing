Programming assignment 3 - use CDK to deploy the resources in Assignment 2

This assignment has exactly the same scenario as Assignment 2. You are asked to use CDK to replace Part 1 and other manual clicks in AWS console. Overall, it includes the following resources:

 - The three lambdas

 - The S3 bucket TestBucket and also the event-triggering relationship b/w the bucket and the size-tracking lambda 

 - The DynamoDB table and the associated secondary index

 - The REST API 

Try to divide it into a reasonable number of stacks, instead of a huge single stack! Also do not hardcode any resource's name.

 

Logistics

1. Upload your code (your CDK project) to GradeScope

 

Demo steps:

  0. Make sure you use cdk destory to delete all the stacks and the associated resources before the demo. Penalty will be applied if your demo exceeds your assigned time. In particular, the demo is solely for grading purpose, please do not debug if you run into any errors.
Deploy the stacks. 
Go to the Cloudformation console and show the stacks. TA - please check the stack creation timestamp.
TA - please check that under the resources tab of the stacks, it collectively show three lambdas, one S3 bucket, one Dynamodb table, one REST API.
Manually invoke the newly created driver lambda in AWS console. TA - please check the contents of the DDB table, also check the newly generated plot.