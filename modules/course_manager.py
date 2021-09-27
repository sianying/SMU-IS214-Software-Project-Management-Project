import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"

class Course:
    def __init__(self, course_id, course_name, prerequisite_course = [],class_list = []):
        self.__course_id = course_name
        self.__course_name = course_name
        self.__class_list = class_list # stores a list of primary keys for the class objects
        self.__prerequisite_course = prerequisite_course # stores a list of primary keys for the course objects
    
    def __init__(self, course_dict):
        self.__course_id = course_dict['course_id']
        self.__course_name = course_dict['course_name']
        self.__class_list = course_dict['class_list']
        self.__prerequisite_course = course_dict['prerequisite_course']

    def get_course_id(self):
        return self.__course_id
    
    def get_course_name(self):
        return self.__course_name

    def get_class_list(self):
        return self.__class_list

    def get_prerequisite_course(self):
        return self.__prerequisite_course

    def add_class(self, class_object):
        self.__class_list.append(class_object)

    def add_prerequisite_course(self, course_obj_pri_key):
        self.__prerequisite_course.append(course_obj_pri_key)

class CourseDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb').Table('Course')
    
    #Create
    def insert_course(self, course_id, course_name, class_list, prerequisite_course):
        # method takes in course variables, insert it to DB and return a Course object
        try: 
            response = self.table.put_item(
                Item = {
                    "course_id": course_id,
                    "course_name": course_name,
                    "prerequisite_course": prerequisite_course,
                    "class_list": class_list
                },
                ConditionExpression=Attr("course_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Course Added'
            return 'Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            return "Course Already Exists"
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
    def update_course(self, Course):
        # method updates the DB if there is new prereq course, removing of prereq course, adding new class
        # assumes course_id and course_name cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'course_id': Course.get_course_id(),
                    'course_name': Course.get_course_name()
                },
                UpdateExpression= "set prerequisite_course = :p, class_list = :c",
                ExpressionAttributeValues ={
                    ":p": Course.get_prerequisite_course(),
                    ':c': Course.get_class_list()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Course Update'
            return 'Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
            
        except Exception as e:
            return "Update Failure with Exception: "+str(e)

    #Delete
    def delete_course(self, Course):
        try:
            response = self.table.delete_item(
                Key = {
                    'course_id': Course.get_course_id(),
                    'course_name': Course.get_course_name()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Course Deleted'
            return 'Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            return "Delete Failure with Exception: "+str(e)


if __name__ == "__main__":
    dao = CourseDAO()
    # print(dao.retrieve_all())
    # print(dao.retrieve_one("IS111").get_prerequisite_course())
    # is111 = dao.retrieve_one("IS111")
    # is111.add_class(1)
    # print(dao.update_course(is111))
    # print(dao.insert_course("IS110","test_course",[],[]))
    # is110 = dao.retrieve_one("IS110")
    # print(dao.delete_course(is110))