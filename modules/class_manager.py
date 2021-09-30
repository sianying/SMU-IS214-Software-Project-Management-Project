import boto3
import os
from boto3.dynamodb.conditions import Key, Attr, Size
from datetime import datetime

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = "../aws_credentials"

class Class:
    def __init__(self, *args, **kwargs):
        '''__init__(
            course_id: Course
            class_id: Integer, 
            start_datetime: DateTime, 
            end_datetime: DateTime, 
            class_size: Integer , 
            trainer_assigned=None: staff_id, 
            learners_enrolled = []: List 
            section_list = []: List
            )

            __init__(class_dict)
        '''
        if len(args) > 1:
            self.__course_id = args[0]
            self.__class_id = args[1]
            self.__start_datetime = args[2]
            if isinstance(self.__start_datetime, str):
                self.__start_datetime = datetime.strptime(self.__start_datetime, "%Y-%m-%dT%H:%M:%S")

            self.__end_datetime = args[3]
            if isinstance(self.__end_datetime, str):
                self.__end_datetime = datetime.strptime(self.__end_datetime, "%Y-%m-%dT%H:%M:%S")

            self.__class_size = args[4]
            try:
                self.__trainer_assigned = kwargs['trainer_assigned']
            except:
                self.__trainer_assigned = None
            try:
                self.__learners_enrolled = kwargs['learners_enrolled']
            except:
                self.__learners_enrolled = []
            try:
                self.__section_list = kwargs['section_list']
            except:
                self.__section_list = []
        elif isinstance(args[0], dict):
            self.__course_id = args[0]['course_id']
            self.__class_id = args[0]['class_id']
            self.__start_datetime = args[0]['start_datetime']
            if isinstance(self.__start_datetime, str):
                self.__start_datetime = datetime.strptime(self.__start_datetime, "%Y-%m-%dT%H:%M:%S")

            self.__end_datetime = args[0]['end_datetime']
            if isinstance(self.__end_datetime, str):
                self.__end_datetime = datetime.strptime(self.__end_datetime, "%Y-%m-%dT%H:%M:%S")
            
            self.__class_size = args[0]['class_size']
            self.__trainer_assigned = args[0]['trainer_assigned']
            self.__learners_enrolled = args[0]['learners_enrolled']
            self.__section_list = args[0]['section_list']

    # Getter Methods
    def get_course_id(self):
        return self.__course_id

    def get_class_id(self):
        return self.__class_id
    
    def get_start_datetime(self):
        return self.__start_datetime
    
    def get_end_datetime(self):
        return self.__end_datetime
    
    def get_class_size(self):
        return self.__class_size
    
    def get_trainer_assigned(self):
        return self.__trainer_assigned
    
    def get_learners_enrolled(self):
        return self.__learners_enrolled
    
    def get_section_list(self):
        return self.__section_list
    
    # Setter Methods
    def set_class_size(self, size):
        self.__class_size = Size
    
    def set_trainer(self, trainer):
        self.__trainer_assigned = trainer
    
    def set_start_datetime(self, start_datetime):
        self.__start_datetime = start_datetime
    
    def set_end_datetime(self, end_datetime):
        self.__end_datetime = end_datetime
    
    def add_section(self, section):
        self.__section_list.append(section)
    
    def enrol_learner(self, staff):
        self.__learners_enrolled.append(staff)
    
    def remove_section(self, section):
        self.__section_list.remove(section)
    
    def json(self):
        return {
            "course_id": self.get_course_id(),
            "class_id": self.get_class_id(),
            "start_datetime": self.get_start_datetime(),
            "end_datetime": self.get_end_datetime(),
            "class_size": self.get_class_size(),
            "trainer_assigned": self.get_trainer_assigned(),
            "learners_enrolled": self.get_learners_enrolled(),
            "section_list": self.get_section_list(),
        }


class ClassDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb').Table('Class')

    #Create
    def insert_class(self, course_id, class_id, start_datetime, end_datetime, class_size, trainer_assigned = None, learners_enrolled= [], section_list=[]):
        try:
            response = self.table.put_item(
                Item = {
                    "class_id": class_id,
                    "start_datetime": start_datetime.isoformat(),
                    'end_datetime' : end_datetime.isoformat(),
                    'class_size': class_size,
                    'trainer_assigned': trainer_assigned,
                    'learners_enrolled': learners_enrolled,
                    "section_list": section_list,
                    "course_id": course_id
                },
                ConditionExpression=Attr("course_id").not_exists() & Attr('class_id').not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Class(course_id, class_id, start_datetime, end_datetime, class_size, trainer_assigned = trainer_assigned, learners_enrolled=learners_enrolled, section_list= section_list)
            return 'Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            return "Class Already Exists"
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

        return [Class(item) for item in response['Items']]
    
    def retrieve_one(self, course_id, class_id):
        response = self.table.get_item(Key={'course_id': course_id, 'class_id': class_id})
        
        if response['Items'] == []:
            return []
        
        return Class(response['Items'][0])

    def retrieve_all_from_course(self, course_id):
        response = self.table.query(KeyConditionExpression=Key('course_id').eq(course_id))

        if response['Items'] == []:
            return []
    
        return [Class(item) for item in response['Items']]

    #Update
    def update_class(self, ClassObj):
        # method updates the DB if there is new prereq course, removing of prereq course, adding new class
        # assumes course_id and course_name cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'course_id': ClassObj.get_course_id(),
                    'class_id': ClassObj.get_class_id()
                },
                UpdateExpression= "set class_size = :s, trainer_assigned = :t, learners_enrolled = :l, section_list = :sec_list, start_datetime = :start, end_datetime = :end",
                ExpressionAttributeValues ={
                    ":s": ClassObj.get_class_size(),
                    ':t': ClassObj.get_trainer_assigned(),
                    ':l': ClassObj.get_learners_enrolled(),
                    ':sec_list': ClassObj.get_section_list(),
                    ':start': ClassObj.get_start_datetime().isoformat(),
                    ':end': ClassObj.get_end_datetime().isoformat(),
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Class Updated'
            return 'Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
            
        except Exception as e:
            return "Update Failure with Exception: "+str(e)

    #Delete
    def delete_class(self, ClassObj):
        try:
            response = self.table.delete_item(
                Key = {
                    'course_id': ClassObj.get_course_id(),
                    'class_id': ClassObj.get_class_id()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Class Deleted'
            return 'Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            return "Delete Failure with Exception: "+str(e)

if __name__ == "__main__":
    dao = ClassDAO()
    # print(dao.retrieve_all())
    # print(dao.insert_class("IS111",2, datetime(2021,9,27,8,0,0), datetime(2021,10,27,8,0,0), 40))

    # class1 = dao.retrieve_all()[0]
    # print(dao.delete_class(class1))
    # print(class1.get_start_datetime())
    # class1.set_start_datetime(datetime(2021,9,28,16,0,0))
    # print(class1.get_start_datetime())
    # print(dao.update_class(class1))