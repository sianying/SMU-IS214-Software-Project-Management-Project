import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import copy
try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")

class Course:
    def __init__(self, course_dict):
        '''
            __init__(course_dict)
            course_dict = {
                course_id: String, 
                course_name: String,
                course_description: String, 
                class_list = []: List, 
                prerequisite_course = []: List 
            }
        '''
        self.__course_id = course_dict['course_id']
        self.__course_name = course_dict['course_name']
        self.__course_description = course_dict['course_description']
        self.__class_list = [int(class_id) for class_id in course_dict['class_list']] if 'class_list' in course_dict else []
        self.__prerequisite_course = copy.deepcopy(course_dict['prerequisite_course']) if 'prerequisite_course' in course_dict else []

    # Getter Methods
    def get_course_id(self):
        return self.__course_id
    
    def get_course_name(self):
        return self.__course_name

    def get_course_description(self):
        return self.__course_description

    def get_class_list(self):
        return self.__class_list

    def get_prerequisite_course(self):
        return self.__prerequisite_course

    # Setter Methods
    def add_class(self, class_id):
        self.__class_list.append(int(class_id))

    def add_prerequisite_course(self, course_id):
        self.__prerequisite_course.append(course_id)

    def check_eligible(self, courses_completed):
        for course in self.get_prerequisite_course():
            if course not in courses_completed:
                return False
        return True

    def json(self):
        return {
            "course_id": self.get_course_id(),
            "course_name": self.get_course_name(),
            "course_description": self.get_course_description(),
            "class_list": self.get_class_list(),
            "prerequisite_course": self.get_prerequisite_course()
        }

class CourseDAO:
    def __init__(self):
        self.table = session.resource('dynamodb', region_name='ap-southeast-1').Table('Course')
    
    #Create    
    def insert_course_w_dict(self, course_dict):
        try:
            if 'class_list' not in course_dict:
                course_dict['class_list'] = []
            
            if 'prerequisite_course' not in course_dict:
                course_dict['prerequisite_course'] = []

            response = self.table.put_item(
                Item = {
                    "course_id": course_dict['course_id'],
                    "course_name": course_dict['course_name'],
                    "course_description": course_dict['course_description'],
                    "prerequisite_course": course_dict['prerequisite_course'],
                    "class_list": course_dict['class_list']
                },
                ConditionExpression=Attr("course_id").not_exists(),
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Course(course_dict)
            raise ValueError('Insert Failure with course_id: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Course already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))

    #Read
    def retrieve_all(self):
        # retrieve all items and add them to a list of Course objects
        response = self.table.scan()
        course_list = response['Items']

        # When last evaluated key is present in response it means the results return exceeds the scan limits -> recall scan and explicitly include the key to start at
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            course_list.extend(response['Items'])

        return [Course(item) for item in course_list]
    
    def retrieve_one(self, course_id):
        response = self.table.query(KeyConditionExpression=Key('course_id').eq(course_id))
        
        if response['Items'] == []:
            return
        
        return Course(response['Items'][0])

    def retrieve_all_in_list(self, course_list):
        try:
            response = self.table.scan(
                FilterExpression=Attr("course_id").is_in(course_list)
            )
            course_list = response['Items']

            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    FilterExpression= Attr("course_id").is_in(course_list),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                course_list.extend(response['Items'])
            
            return [Course(item) for item in course_list]
        except Exception as e:
            raise ValueError("List entered is empty")

    def retrieve_all_not_in_list(self, course_list):
        try:
            response = self.table.scan(
                FilterExpression=~Attr("course_id").is_in(course_list)
            )
            course_list = response['Items']

            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    FilterExpression=~Attr("course_id").is_in(course_list),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                course_list.extend(response['Items'])
            
            return [Course(item) for item in course_list]
        except Exception as e:
            raise ValueError("List entered is empty")

    def retrieve_eligible_course(self, courses_completed, courses_enrolled_or_teaching):
        try:
            course_list = self.retrieve_all_not_in_list(courses_completed+courses_enrolled_or_teaching)
        except ValueError:
            course_list = self.retrieve_all()
        
        result_list = []
        for course in course_list:
            if course.check_eligible(courses_completed):
                result_list.append(course)

        return result_list
    
    #Update
    def update_course(self, CourseObj):
        # method updates the DB if there is new prereq course, removing of prereq course, adding new class
        # assumes course_id and course_name cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'course_id': CourseObj.get_course_id(),
                },
                UpdateExpression= "set prerequisite_course = :p, class_list = :c",
                ExpressionAttributeValues ={
                    ":p": CourseObj.get_prerequisite_course(),
                    ':c': CourseObj.get_class_list()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Course Updated'
            raise ValueError('Update Failure with course_id: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
            
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))

