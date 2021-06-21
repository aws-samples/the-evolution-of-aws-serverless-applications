import json
import logging
import pymysql
import boto3
import base64
from botocore.exceptions import ClientError

secret_name = "serverless-app-rds-secret"
region_name = "ap-northeast-2"

def lambda_handler(event, context):
    secret = get_secret()
    json_secret = json.loads(secret)

    db = pymysql.connect(
        host = 'your rds proxy endpoint', 
        user = json_secret['username'], 
        password = json_secret['password']
        )

    cursor = db.cursor()
    
    cursor.execute("select now()")
    result = cursor.fetchone()

    db.commit()
    db.close()
    
    return {
        'statusCode': 200,
        'body': json.dumps(result[0].isoformat())
    }


def get_secret():    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name = region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret