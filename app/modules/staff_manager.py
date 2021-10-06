import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4
import copy
try:
    from course_manager import CourseDAO
except:
    from modules.course_manager import CourseDAO

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
                self.__courses_completed = copy.deepcopy(kwargs['courses_completed'])
            except:
                self.__courses_completed = []
            
            try:
                self.__courses_enrolled = copy.deepcopy(kwargs['courses_enrolled'])
            except:
                self.__courses_enrolled = []
        elif isinstance(args[0], dict):
            self.__staff_id = args[0]['staff_id']
            self.__staff_name = args[0]['staff_name']
            self.__role = args[0]['role']
            self.__courses_enrolled = copy.deepcopy(args[0]['courses_enrolled'])
            self.__courses_completed = copy.deepcopy(args[0]['courses_completed'])
        
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
        if course in self.__courses_completed:
            raise ValueError(str(course)+" already completed")
        self.__courses_completed.append(course)
    
    def add_enrolled(self, course):
        if course in self.__courses_enrolled:
            raise ValueError("Already enrolled in "+str(course))
        self.__courses_enrolled.append(course)
    
    def remove_enrolled(self, course):
        self.__courses_enrolled.remove(course)

    def json(self):
        return {
            "staff_id": self.get_staff_id(),
            "staff_name": self.get_staff_name(),
            "role": self.get_role(),
            "courses_completed": self.get_courses_completed(),
            "courses_enrolled": self.get_courses_enrolled(),
        }

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
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Staff already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))
    
    def insert_staff_w_dict(self, staff_dict):
        try:
            if 'staff_id' not in staff_dict or staff_dict['staff_id'] == None:
                staff_dict['staff_id'] = str(uuid4())
            
            if 'courses_completed' not in staff_dict:
                staff_dict['courses_completed'] = []

            if 'courses_enrolled' not in staff_dict:
                staff_dict['courses_enrolled'] = []

            response = self.table.put_item(
                Item = {
                    "staff_id": staff_dict['staff_id'],
                    "staff_name": staff_dict['staff_name'],
                    'role' : staff_dict['role'],
                    'courses_completed': staff_dict['courses_completed'],
                    'courses_enrolled': staff_dict['courses_enrolled']
                },
                ConditionExpression=Attr("staff_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Staff(staff_dict)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Staff already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))

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

    def retrieve_all_courses_enrolled(self, staff_id):
        staff = self.retrieve_one(staff_id)
        course_id_list = staff.get_courses_enrolled()
        dao = CourseDAO()        
        return dao.retrieve_all_in_list(course_id_list)

    def retrieve_all_eligible_to_enroll(self, staff_id):
        staff = self.retrieve_one(staff_id)
        dao = CourseDAO()
        return dao.retrieve_eligible_course(staff.get_courses_completed(), staff.get_courses_enrolled())

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
    # course_list = dao.retrieve_all_courses_enrolled("6724873a-b951-4ee7-a835-cb0f9f784c45")
    # print([course.json() for course in course_list])
