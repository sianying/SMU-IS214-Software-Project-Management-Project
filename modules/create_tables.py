import boto3
import os
os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./aws_credentials"


def create_course_table():
    try:
        table = dynamodb.create_table(
            TableName='Course',
            KeySchema=[
                {
                    'AttributeName': 'course_id',
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'course_name',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'course_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'course_name',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits':5,
                'WriteCapacityUnits':5
            }
        )
    except Exception as e:
        return e
    return "Table Created"

def create_class_table():
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Class',
            KeySchema=[
                {
                    'AttributeName': 'course_id', 
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'class_id',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'course_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'class_id',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits':5,
                'WriteCapacityUnits':5
            }
        )
    except Exception as e:
        return e
    return "Table Created"

def create_section_table():
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Section',
            KeySchema=[
                {
                    'AttributeName': 'course_id', 
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'class_id',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'course_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'class_id',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'section_id',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'section_name',
                    'AttributeType': 'S'
                },
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": 'SectionIndex',
                    "KeySchema": [
                        {
                            'AttributeName': 'section_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'section_name',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection':{
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput':{
                        "ReadCapacityUnits":1,
                        "WriteCapacityUnits":1
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits':5,
                'WriteCapacityUnits':5
            }
            
        )
    except Exception as e:
        return e
    return "Table Created"

def create_quiz_table():
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Quiz',
            KeySchema=[
                {
                    'AttributeName': 'course_id', 
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'class_id',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'course_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'class_id',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'section_id',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'section_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'mat_name',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": 'SectionIndex',
                    "KeySchema": [
                        {
                            'AttributeName': 'section_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'section_name',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection':{
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput':{
                        "ReadCapacityUnits":1,
                        "WriteCapacityUnits":1
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits':5,
                'WriteCapacityUnits':5
            }
            
        )
    except Exception as e:
        return e
    return "Table Created"



if __name__ == "__main__":
    dynamodb = boto3.resource('dynamodb')
    course_table = create_course_table()
    class_table = create_class_table()
    section_table = create_section_table()
    print("Table status:", course_table)
    print("Table status:", class_table)
    print("Table status:", section_table)