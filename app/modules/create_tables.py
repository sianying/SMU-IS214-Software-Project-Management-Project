import boto3
import os
try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")


def create_course_table(dynamodb):
    try:
        table = dynamodb.create_table(
            TableName='Course',
            KeySchema=[
                {
                    'AttributeName': 'course_id',
                    'KeyType': 'HASH' # Partition Key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'course_id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits':2,
                'WriteCapacityUnits':2
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
                'ReadCapacityUnits':2,
                'WriteCapacityUnits':2
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
                'ReadCapacityUnits':2,
                'WriteCapacityUnits':2
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
                    'AttributeName': 'quiz_id',
                    'KeyType': 'HASH' # Partition key
                },
                {
                    'AttributeName': 'section_id',
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
            GlobalSecondaryIndexes=[
                {
                    "IndexName": 'SectionIndex',
                    "KeySchema": [
                        {
                            'AttributeName': 'section_id',
                            'KeyType': 'HASH'
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
                'ReadCapacityUnits':2,
                'WriteCapacityUnits':2
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
                    'AttributeName': 'attempt_uuid',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'quiz_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'attempt_uuid',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'staff_id',
                    'AttributeType': 'S'
                }
            ], 
            GlobalSecondaryIndexes=[
                {
                    "IndexName": 'StaffIndex',
                    "KeySchema": [
                        {
                            'AttributeName': 'quiz_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'staff_id',
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
                'ReadCapacityUnits':2,
                'WriteCapacityUnits':2
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
                'ReadCapacityUnits':2,
                'WriteCapacityUnits':2
            }
            
        )
    except Exception as e:
        return e
    return "Table Created"

def create_request_table(dynamodb):
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Request',
            KeySchema=[
                {
                    'AttributeName': 'staff_id',
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'course_id',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'staff_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'course_id',
                    'AttributeType': 'S'
                },
                {
                    "AttributeName": 'req_status',
                    'AttributeType': 'S'
                }
            ], 
            GlobalSecondaryIndexes=[
                {
                    "IndexName": 'StatusIndex',
                    "KeySchema": [
                        {
                            'AttributeName': 'req_status',
                            'KeyType': 'HASH'
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
                'ReadCapacityUnits':2,
                'WriteCapacityUnits':2
            }
            
        )
    except Exception as e:
        return e
    return "Table Created"


def create_progress_table(dynamodb):
    try:
        # Data in with same partition key are stored together sorted by sort key value
        table = dynamodb.create_table(
            TableName='Progress',
            KeySchema=[
                {
                    'AttributeName': 'staff_id',
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'course_id',
                    'KeyType': 'RANGE' # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'staff_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'course_id',
                    'AttributeType': 'S'
                },
            ], 
            ProvisionedThroughput={
                'ReadCapacityUnits':2,
                'WriteCapacityUnits':2
            }
        )
    except Exception as e:
        return e
    return "Table Created"




if __name__ == "__main__":
    dynamodb = session.resource('dynamodb', region_name='ap-southeast-1')
    course_table = create_course_table(dynamodb)
    class_table = create_class_table(dynamodb)
    section_table = create_section_table(dynamodb)
    quiz_table = create_quiz_table(dynamodb)
    attempt_table = create_attempt_table(dynamodb)
    staff_table = create_staff_table(dynamodb)
    request_table = create_request_table(dynamodb)
    progress_table = create_progress_table(dynamodb)

    print("Course Table status:", course_table)
    print("Class Table status:", class_table)
    print("Section Table status:", section_table)
    print("Quiz Table status:", quiz_table)
    print("Attempt Table status:", attempt_table)
    print("Staff Table status:", staff_table)
    print("Request Table status:", request_table)
    print("Progress Table status:", progress_table)