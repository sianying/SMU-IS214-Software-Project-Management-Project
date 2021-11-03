import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4
import copy

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")


class Staff:
    def __init__(self, staff_dict):
        '''
            __init__(
                staff_id: int,
                staff_name: String,
                role: String,
                isTrainer: Boolean (0/1),
                courses_completed = []: List,
                courses_enrolled = []: List
            )

            __init__(staff_dict)
        '''
        self.__staff_id = staff_dict['staff_id']
        self.__staff_name = staff_dict['staff_name']
        self.__role = staff_dict['role']
        self.__isTrainer = staff_dict['isTrainer']
        self.__courses_enrolled = copy.deepcopy(staff_dict['courses_enrolled']) if 'courses_enrolled' in staff_dict else []
        self.__courses_completed = copy.deepcopy(staff_dict['courses_completed']) if 'courses_completed' in staff_dict else []


    def get_staff_id(self):
        return self.__staff_id
    
    def get_staff_name(self):
        return self.__staff_name
    
    def get_role(self):
        return self.__role

    def get_isTrainer(self):
        return self.__isTrainer
    
    def get_courses_completed(self):
        return self.__courses_completed
    
    def get_courses_enrolled(self):
        return self.__courses_enrolled

    def convert_trainer(self):
        if self.__isTrainer:
            raise ValueError("Staff is already a Trainer")
        self.__isTrainer = 1    
    
    def add_completed(self, course):
        if course in self.__courses_completed:
            raise ValueError(str(course) + " already completed")
        self.__courses_completed.append(course)
    
    def add_enrolled(self, course):
        if course in self.__courses_completed:
            raise ValueError(str(course) + " already completed")

        if course in self.__courses_enrolled:
            raise ValueError("Already enrolled in " +str(course))
        self.__courses_enrolled.append(course)
    
    def remove_enrolled(self, course):
        self.__courses_enrolled.remove(course)

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
            "isTrainer": self.get_isTrainer(),
            "courses_completed": self.get_courses_completed(),
            "courses_enrolled": self.get_courses_enrolled(),
        }


class StaffDAO:
    def __init__(self):
        self.table = session.resource('dynamodb', region_name='ap-southeast-1').Table('Staff')

    #Create
    def insert_staff_w_dict(self, staff_dict):
        try:
            if 'staff_id' not in staff_dict or staff_dict['staff_id'] == None:
                staff_dict['staff_id'] = str(uuid4())

            if 'isTrainer' not in staff_dict:
                staff_dict['isTrainer'] = 0
            
            if 'courses_completed' not in staff_dict:
                staff_dict['courses_completed'] = []

            if 'courses_enrolled' not in staff_dict:
                staff_dict['courses_enrolled'] = []

            response = self.table.put_item(
                Item = {
                    "staff_id": staff_dict['staff_id'],
                    "staff_name": staff_dict['staff_name'],
                    'role' : staff_dict['role'],
                    'isTrainer': staff_dict['isTrainer'],
                    'courses_completed': staff_dict['courses_completed'],
                    'courses_enrolled': staff_dict['courses_enrolled'],
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
        # assumes staff_id, staff_name and role cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'staff_id': StaffObj.get_staff_id(),
                    'staff_name': StaffObj.get_staff_name(),
                },
                UpdateExpression= "set courses_completed = :c, courses_enrolled = :e",
                ExpressionAttributeValues ={
                    ":c": StaffObj.get_courses_completed(),
                    ':e': StaffObj.get_courses_enrolled(),
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Staff Updated'
            raise ValueError('Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
            
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))
