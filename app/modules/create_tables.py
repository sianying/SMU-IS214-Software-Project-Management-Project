import boto3
import os
os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"

def create_course_table(dynamodb):
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

def create_class_table(dynamodb):
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

def create_section_table(dynamodb):
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Section',
            KeySchema=[
                {
                    'AttributeName': 'section_id', 
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
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": 'CourseIndex',
                    "KeySchema": [
                        {
                            'AttributeName': 'course_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'class_id',
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

def create_quiz_table(dynamodb):
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Quiz',
            KeySchema=[
                {
                    'AttributeName': 'section_id',
                    'KeyType': 'HASH' # Sort key
                },
                {
                    'AttributeName': 'quiz_id',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'section_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'quiz_id',
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

def create_material_table(dynamodb):
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Material',
            KeySchema=[
                {
                    'AttributeName': 'section_id', 
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'material_id',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'section_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'material_id',
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

def create_attempt_table(dynamodb):
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Attempt',
            KeySchema=[
                {
                    'AttributeName': 'quiz_id', 
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'staff_id',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'quiz_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'staff_id',
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

def create_staff_table(dynamodb):
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Staff',
            KeySchema=[
                {
                    'AttributeName': 'staff_id', 
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'staff_name',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'staff_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'staff_name',
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


if __name__ == "__main__":
    dynamodb = boto3.resource('dynamodb')
    course_table = create_course_table(dynamodb)
    class_table = create_class_table(dynamodb)
    section_table = create_section_table(dynamodb)
    quiz_table = create_quiz_table(dynamodb)
    material_table = create_material_table(dynamodb)
    attempt_table = create_attempt_table(dynamodb)
    staff_table = create_staff_table(dynamodb)
    print("Course Table status:", course_table)
    print("Class Table status:", class_table)
    print("Section Table status:", section_table)
    print("Quiz Table status:", quiz_table)
    print("Material Table status:", material_table)
    print("Attempt Table status:", attempt_table)
    print("Staff Table status:", staff_table)