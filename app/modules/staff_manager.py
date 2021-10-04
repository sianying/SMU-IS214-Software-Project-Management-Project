import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = "../aws_credentials"

class Staff:
    def __init__(self, *args, **kwargs):
        '''
            __init__(
                staff_id: int,
                staff_name: String,
                role: String,
                courses_completed = []: List,
                courses_enrolled = []: List
            )

            __init__(staff_dict)
        '''

        if len(args) > 1:
            self.__staff_id = args[0]
            self.__staff_name = args[1]
            self.__role = args[2]
            try:
                self.__courses_completed = kwargs['courses_completed']
            except:
                self.__courses_completed = []
            
            try:
                self.__courses_enrolled = kwargs['courses_enrolled']
            except:
                self.__courses_enrolled = []
        elif isinstance(args[0], dict):
            self.__staff_id = args[0]['staff_id']
            self.__staff_name = args[0]['staff_name']
            self.__role = args[0]['role']
            self.__courses_enrolled = args[0]['courses_enrolled']
            self.__courses_completed = args[0]['courses_completed']
        
    def get_staff_id(self):
        return self.__staff_id
    
    def get_staff_name(self):
        return self.__staff_name
    
    def get_role(self):
        return self.__role
    
    def get_courses_completed(self):
        return self.__courses_completed
    
    def get_courses_enrolled(self):
        return self.__courses_enrolled
    
    def add_completed(self, course):
        self.__courses_completed.append(course)
    
    def add_enrolled(self, course):
        self.__courses_enrolled.append(course)
    
    def remove_enrolled(self, course):
        self.__courses_enrolled.remove(course)

class StaffDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb', region_name="us-east-1").Table('Staff')

    #Create
    def insert_staff(self, staff_name, role, staff_id = None, courses_completed= [], courses_enrolled = []):
        try:
            if staff_id == None:
                staff_id = str(uuid4())
            response = self.table.put_item(
                Item = {
                    "staff_id": staff_id,
                    "staff_name": staff_name,
                    'role' : role,
                    'courses_completed': courses_completed,
                    'courses_enrolled': courses_enrolled
                },
                ConditionExpression=Attr("staff_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Staff(staff_id, staff_name, role, courses_completed=courses_completed, courses_enrolled=courses_enrolled)
            return 'Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            return "Staff Already Exists"
        except Exception as e:
            return "Insert Failure with Exception: "+str(e)
    
    #Read
    def retrieve_all(self):
        
        # retrieve all items and add them to a list of Course objects
        response = self.table.scan()
        data = response['Items']

        # When last evaluated key is present in response it means the results return exceeds the scan limits -> recall scan and explicitly include the key to start at
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])

        staff_list = []

        for item in data:
            staff_list.append(Staff(item))

        return staff_list
    
    def retrieve_one(self, staff_id):
        response = self.table.query(KeyConditionExpression=Key('staff_id').eq(staff_id))
        
        if response['Items'] == []:
            return 
        
        return Staff(response['Items'][0])

    #Update
    def update_staff(self, StaffObj):
        # method updates the DB if there is new prereq course, removing of prereq course, adding new class
        # assumes staff_id and course_name cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'staff_id': StaffObj.get_staff_id(),
                    'staff_name': StaffObj.get_staff_name()
                },
                UpdateExpression= "set courses_completed = :c, courses_enrolled = :e",
                ExpressionAttributeValues ={
                    ":c": StaffObj.get_courses_completed(),
                    ':e': StaffObj.get_courses_enrolled(),
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Staff Updated'
            return 'Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
            
        except Exception as e:
            return "Update Failure with Exception: "+str(e)

    #Delete
    def delete_staff(self, StaffObj):
        try:
            response = self.table.delete_item(
                Key = {
                    'staff_id': StaffObj.get_staff_id(),
                    'staff_name': StaffObj.get_staff_name()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Staff Deleted'
            return 'Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            return "Delete Failure with Exception: "+str(e)

if __name__ == "__main__":
    dao = StaffDAO()
    # print(dao.retrieve_all())
    # print(dao.insert_staff("Johnny", "HR"))
    # print(dao.insert_staff("Tom", "Engineer"))
    # staff1 = dao.retrieve_all()[1]
    # print(staff1.get_staff_id())
    # print(dao.delete_staff(staff1))
    # tom = dao.retrieve_one("6724873a-b951-4ee7-a835-cb0f9f784c45")
    # tom.add_completed("IS110")
    # tom.add_enrolled("IS111")
    # print(dao.update_staff(johnny))
    # print(tom.get_courses_enrolled())
    # print(tom.get_courses_completed())

    # for staff in dao.retrieve_all():
    #     print(staff.get_staff_id())