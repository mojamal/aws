#!/usr/bin/env python3

import boto3
import json

# Initialize boto3 Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')

# Function to invoke AWS Lambda asynchronously
def trigger_lambda_async(lambda_function_name, payload):
    try:
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType='Event',  # This ensures async invocation
            Payload=json.dumps(payload),

        )

        # Check response for any issues
        if response['StatusCode'] == 202:
            print("Lambda function "+lambda_function_name+" invoked successfully.")
        else:
            print("Failed to invoke Lambda function. StatusCode: "+str(response['StatusCode']))

    except Exception as e:
        print("Error invoking Lambda: "+str(e))


# Replace with your Lambda function name
lambda_function_name = 'arn:aws:lambda:us-east-1:<your AWS Account#>:function:CheckFileEncoding'

# Payload to send to the Lambda function
payload = {
  "s3_bucket": "support-center-logs-dev",
  "s3_file": "transcripts/2026-01-05/incident312588.txt"
}

# Trigger Lambda asynchronously
trigger_lambda_async(lambda_function_name, payload)
