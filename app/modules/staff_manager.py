import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4
import copy

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
                courses_can_teach = []: List
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

            try:
                self.__courses_can_teach = copy.deepcopy(kwargs['courses_can_teach'])
            except:
                self.__courses_can_teach = []

        elif isinstance(args[0], dict):
            self.__staff_id = args[0]['staff_id']
            self.__staff_name = args[0]['staff_name']
            self.__role = args[0]['role']
            self.__courses_enrolled = copy.deepcopy(args[0]['courses_enrolled'])
            self.__courses_completed = copy.deepcopy(args[0]['courses_completed'])
            self.__courses_can_teach = copy.deepcopy(args[0]['courses_can_teach'])
        
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

    def get_courses_can_teach(self):
        return self.__courses_can_teach
    
    def add_completed(self, course):
        if course in self.__courses_completed:
            raise ValueError(str(course)+" already completed")
        self.__courses_completed.append(course)
    
    def add_enrolled(self, course):
        if course in self.__courses_completed:
            raise ValueError(str(course) + " already completed")

        if course in self.__courses_enrolled:
            raise ValueError("Already enrolled in "+str(course))
        self.__courses_enrolled.append(course)
    
    def remove_enrolled(self, course):
        self.__courses_enrolled.remove(course)

    def add_can_teach(self, course):
        if course in self.__courses_can_teach:
            raise ValueError(str(course)+" has already been recorded as a teachable course.")
        self.__courses_can_teach.append(course)

    def remove_can_teach(self, course):
        self.__courses_can_teach.remove(course)

    def can_enrol(self, course_id_to_enroll, prerequisite_list):
        if course_id_to_enroll in self.get_courses_completed() or course_id_to_enroll in self.get_courses_enrolled():
            return False
        
        completed_list = self.get_courses_completed()

        for course in prerequisite_list:
            if course not in completed_list:
                return False
        
        return True

    def json(self):
        return {
            "staff_id": self.get_staff_id(),
            "staff_name": self.get_staff_name(),
            "role": self.get_role(),
            "courses_completed": self.get_courses_completed(),
            "courses_enrolled": self.get_courses_enrolled(),
            "courses_can_teach": self.get_courses_can_teach()
        }

class StaffDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb', region_name="ap-southeast-1").Table('Staff')

    #Create
    def insert_staff(self, staff_name, role, staff_id = None, courses_completed= [], courses_enrolled = [], courses_can_teach=[]):
        try:
            if staff_id == None:
                staff_id = str(uuid4())
            response = self.table.put_item(
                Item = {
                    "staff_id": staff_id,
                    "staff_name": staff_name,
                    'role' : role,
                    'courses_completed': courses_completed,
                    'courses_enrolled': courses_enrolled,
                    'courses_can_teach': courses_can_teach
                },
                ConditionExpression=Attr("staff_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Staff(staff_id, staff_name, role, courses_completed=courses_completed, courses_enrolled=courses_enrolled, courses_can_teach=courses_can_teach)
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

            if 'courses_can_teach' not in staff_dict:
                staff_dict['courses_can_teach'] = []

            response = self.table.put_item(
                Item = {
                    "staff_id": staff_dict['staff_id'],
                    "staff_name": staff_dict['staff_name'],
                    'role' : staff_dict['role'],
                    'courses_completed': staff_dict['courses_completed'],
                    'courses_enrolled': staff_dict['courses_enrolled'],
                    'courses_can_teach': staff_dict['courses_can_teach']
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

    def retrieve_all_trainers_can_teach(self, course_id):
        staff_list = self.retrieve_all()

        returned_list=[]
        for staff in staff_list:
            courses_can_teach = staff.get_courses_can_teach()
            if course_id in courses_can_teach:
                returned_list.append(staff)

        return returned_list

    def retrieve_eligible_staff_to_enrol(self, courseObj):
        staff_list = self.retrieve_all()
        prereq_course = courseObj.get_prerequisite_course()
        course_id_to_enroll = courseObj.get_course_id()

        result_list = []
        for staff in staff_list:
            if staff.can_enrol(course_id_to_enroll, prereq_course):
                result_list.append(staff)
        
        return result_list

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
                UpdateExpression= "set courses_completed = :c, courses_enrolled = :e, courses_can_teach = :t",
                ExpressionAttributeValues ={
                    ":r": StaffObj.get_role(),
                    ":c": StaffObj.get_courses_completed(),
                    ':e': StaffObj.get_courses_enrolled(),
                    ':t': StaffObj.get_courses_can_teach()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Staff Updated'
            raise ValueError('Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
            
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))



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
            raise ValueError('Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise ValueError("Delete Failure with Exception: "+str(e))

if __name__ == "__main__":
    dao = StaffDAO()