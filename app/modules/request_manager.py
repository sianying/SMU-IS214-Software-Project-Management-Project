import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")

class Request:

    def __init__(self, *args):
        '''
            __init__(
                course_id: String,
                class_id: Integer,
                staff_id: String,
                req_status = 'pending': String
            )

            __init__(request_dict)
        '''

        if len(args) > 1:
            self.__course_id = args[0]
            self.__class_id = int(args[1])
            self.__staff_id = args[2]
            try: 
                self.__req_status = args[3]
            except:
                self.__req_status = 'pending'
        elif isinstance(args[0], dict):
            self.__course_id = args[0]['course_id']
            self.__class_id = int(args[0]['class_id'])
            self.__staff_id = args[0]['staff_id']
            try: 
                self.__req_status = args[0]['req_status']
            except:
                self.__req_status = 'pending'

    def get_course_id(self):
        return self.__course_id
    
    def get_class_id(self):
        return self.__class_id
    
    def get_staff_id(self):
        return self.__staff_id
    
    def get_req_status(self):
        return self.__req_status
    
    def update_req_status(self, status):
        if status not in ['approved', 'rejected']:
            raise ValueError("Status must be either approved or rejected")
        
        self.__req_status = status

    def json(self):
        return {
            'course_id': self.get_course_id(),
            'class_id': self.get_class_id(),
            'staff_id': self.get_staff_id(),
            'req_status': self.get_req_status()
        }

class RequestDAO:
    def __init__(self):
        self.table = session.resource('dynamodb', region_name = 'ap-southeast-1').Table('Request')
    
    #Create
    def insert_request_w_dict(self, request_dict):
        try:
            if 'req_status' not in request_dict:
                request_dict['req_status'] = 'pending'

            response = self.table.put_item(
                Item = {
                    'course_id': request_dict['course_id'],
                    'class_id': request_dict['class_id'],
                    'staff_id': request_dict['staff_id'],
                    'req_status': request_dict['req_status']
                }
            )

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Request(request_dict)
            raise ValueError('Insert Failure with course_id: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+ str(e))
    
    #Read
    def retrieve_all_pending(self):
        response = self.table.query(IndexName='StatusIndex', KeyConditionExpression = Key('req_status').eq("pending"))

        return [Request(item) for item in response['Items']]

    def retrieve_all_from_staff(self, staff_id):
        response = self.table.scan(
            FilterExpression = Attr('staff_id').eq(staff_id)
        )
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                FilterExpression = Attr('staff_id').eq(staff_id),
                ExclusiveStartKey = response['LastEvaluatedKey']
            )
            data.extend(response['Items'])
        
        return [Request(item) for item in data]
    
    #Update
    def update_request(self, requestObj):
        try:
            response = self.table.update_item(
                Key = {
                    'course_id': requestObj.get_course_id(),
                    'staff_id': requestObj.get_staff_id()
                },
                UpdateExpression = "set req_status = :s",
                ExpressionAttributeValues ={
                    ':s': requestObj.get_req_status()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Request Updated'
            raise ValueError('Update Failure with error: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise Exception("Update Failure with Exception: "+ str(e))

if __name__ == "__main__":
    # item = {
    #     "staff_id": "95874dea-a6d1-4f30-9062-61ac85bcfe6a",
    #     "course_id": "IC116",
    #     "class_id": 1,
    #     "req_status": "approved"
    # }
    # item2 ={
    #     "staff_id": "80e6f2f7-2827-4a3d-828a-0fdcea180641",
    #     "course_id": "IC116",
    #     "class_id": 1
    # }
    # dao = RequestDAO()
    # print(dao.insert_request_w_dict(item).json())
    # print(dao.insert_request_w_dict(item2).json())
    # print(dao.update_request(Request(item)))
    # print([a.json() for a in dao.retrieve_all_pending()])
    # print([a.json() for a in dao.retrieve_all_from_staff("95874dea-a6d1-4f30-9062-61ac85bcfe6a")])