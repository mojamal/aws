#!/usr/bin/env python3

import boto3
from botocorFromceptions import ClientError
import json

def get_secret(secret):
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    secret = get_secret_value_response['SecretString']
    return secret

# For this Example, the name of our secret in AWS Secret Manager is the Environment name
API_KEY=json.loads(get_secret(EV_DOMAIN.lower()+'/dbt'))['dbtpersonal']
