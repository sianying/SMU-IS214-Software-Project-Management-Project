import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import copy

os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"

class Course:

    def __init__(self, *args, **kwargs):
        '''__init__(
            course_id: String, 
            course_name: String,
            description: String, 
            class_list = []: List, 
            prerequisite_course = []: List 
            )

            __init__(course_dict)
        '''
        if len(args) > 1:
            self.__course_id = args[0]
            self.__course_name = args[1]
            self.__course_description = args[2]
            try:
                self.__class_list = [int(class_id) for class_id in kwargs['class_list']] # stores a list of primary keys for the class objects
            except:
                self.__class_list = []
            try:
                self.__prerequisite_course = copy.deepcopy(kwargs['prerequisite_course']) # stores a list of primary keys for the course objects
            except:
                self.__prerequisite_course = []
        elif isinstance(args[0], dict):
            self.__course_id = args[0]['course_id']
            self.__course_name = args[0]['course_name']
            self.__course_description = args[0]['course_description']
            self.__class_list = [int(class_id) for class_id in args[0]['class_list']]
            self.__prerequisite_course = copy.deepcopy(args[0]['prerequisite_course'])

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
        self.table = boto3.resource('dynamodb', region_name="us-east-1").Table('Course')
    
    #Create
    def insert_course(self, course_id, course_name, course_description, class_list=[], prerequisite_course=[]):
        try: 
            response = self.table.put_item(
                Item = {
                    "course_id": course_id,
                    "course_name": course_name,
                    "course_description": course_description,
                    "prerequisite_course": prerequisite_course,
                    "class_list": class_list
                },
                ConditionExpression=Attr("course_id").not_exists(),
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Course(course_id, course_name, course_description, class_list=class_list, prerequisite_course=prerequisite_course)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Course already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))
    
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
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Course already exists")
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

        course_list = []

        for item in data:
            course_list.append(Course(item))

        return course_list
    
    def retrieve_one(self, course_id):
        response = self.table.query(KeyConditionExpression=Key('course_id').eq(course_id))
        
        if response['Items'] == []:
            return 
        
        return Course(response['Items'][0])

    #Update
    def update_course(self, CourseObj):
        # method updates the DB if there is new prereq course, removing of prereq course, adding new class
        # assumes course_id and course_name cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'course_id': CourseObj.get_course_id(),
                    'course_name': CourseObj.get_course_name()
                },
                UpdateExpression= "set prerequisite_course = :p, class_list = :c",
                ExpressionAttributeValues ={
                    ":p": CourseObj.get_prerequisite_course(),
                    ':c': CourseObj.get_class_list()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Course Updated'
            raise ValueError('Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
            
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))

    #Delete
    def delete_course(self, CourseObj):
        try:
            response = self.table.delete_item(
                Key = {
                    'course_id': CourseObj.get_course_id(),
                    'course_name': CourseObj.get_course_name()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Course Deleted'
            raise ValueError('Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise Exception("Delete Failure with Exception: "+str(e))


if __name__ == "__main__":
    dao = CourseDAO()
    # course1 = dao.retrieve_all()[0]
    # print(course1.json())
    # print(dao.retrieve_one("IS111").get_prerequisite_course())
    # is111 = dao.retrieve_one("IS111")
    # is111.add_class(1)
    # print(dao.update_course(is111))
    # print(dao.insert_course("IS110","test_course",[],[]))
    # is110 = dao.retrieve_one("IS110")
    # print(dao.delete_course(is110))