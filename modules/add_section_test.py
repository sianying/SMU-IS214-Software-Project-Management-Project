import boto3
import os
from boto3.dynamodb.conditions import Key
os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./aws_credentials"
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('Class')

# response = table.put_item(
#     Item = {
#         'course_id': 'IS111',
#         'class_id': 1,
#         'section_id': 10,
#         'section_name': 'Paper Feeder',
#         'material':[
#             {
#                 'mat_name': 'test material 1',
#                 'mat_type': 'doc',
#                 'url': 'www.google.com'
#             }
#         ],
#         'quiz' : 'quiz-id-12345123'
#     }
# )

# response = table.put_item(
#     Item = {
#         'course_id': 'IS111',
#         'class_id': 1,
#         'section_list': ['section1','section2','section3'],
#     }
# )

# print(response)

# response = table.query(
#     IndexName='MaterialIndex',
#     KeyConditionExpression=Key("mat_name").eq("test material 1")
# )

# print(response)

# response = table.query(KeyConditionExpression = Key('course_id').eq('IS111') & Key('class_id').eq(1))
# print(response['Items'])