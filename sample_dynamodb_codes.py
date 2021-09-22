import boto3
import os

os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./aws_credentials"

dynamodb = boto3.resource('dynamodb')

print(list(dynamodb.tables.all()))