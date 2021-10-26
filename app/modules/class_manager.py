import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import copy

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")


class Class:
    def __init__(self, *args, **kwargs):
        '''__init__(
            course_id: Course
            class_id: Integer, 
            start_datetime: DateTime, 
            end_datetime: DateTime, 
            class_size: Integer, 
            trainer_assigned=None: staff_id, 
            learners_enrolled = []: List 
            section_list = []: List
            )

            __init__(class_dict)
        '''
        if len(args) > 1:
            self.__course_id = args[0]
            self.__class_id = int(args[1])
            self.__start_datetime = args[2]
            if isinstance(self.__start_datetime, str):
                self.__start_datetime = datetime.strptime(self.__start_datetime, "%Y-%m-%dT%H:%M:%S")

            self.__end_datetime = args[3]
            if isinstance(self.__end_datetime, str):
                self.__end_datetime = datetime.strptime(self.__end_datetime, "%Y-%m-%dT%H:%M:%S")

            self.__class_size = int(args[4])
            
            try:
                self.__trainer_assigned = kwargs['trainer_assigned']
            except:
                self.__trainer_assigned = None
            try:
                self.__learners_enrolled = copy.deepcopy(kwargs['learners_enrolled'])
            except:
                self.__learners_enrolled = []
            try:
                self.__section_list = copy.deepcopy(kwargs['section_list'])
            except:
                self.__section_list = []

        elif isinstance(args[0], dict):
            self.__course_id = args[0]['course_id']
            self.__class_id = int(args[0]['class_id'])
            self.__start_datetime = args[0]['start_datetime']
            if isinstance(self.__start_datetime, str):
                self.__start_datetime = datetime.strptime(self.__start_datetime, "%Y-%m-%dT%H:%M:%S")

            self.__end_datetime = args[0]['end_datetime']
            if isinstance(self.__end_datetime, str):
                self.__end_datetime = datetime.strptime(self.__end_datetime, "%Y-%m-%dT%H:%M:%S")

            self.__class_size = int(args[0]['class_size'])
            self.__trainer_assigned = args[0]['trainer_assigned']
            self.__learners_enrolled = copy.deepcopy(args[0]['learners_enrolled'])
            self.__section_list = copy.deepcopy(args[0]['section_list'])

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
        self.__class_size = int(size)
    
    def set_trainer(self, trainer):
        self.__trainer_assigned = trainer
    
    def set_start_datetime(self, start_datetime):
        if isinstance(start_datetime, str):
            start_datetime = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")

        if start_datetime > self.get_end_datetime():
            raise ValueError("Start datetime cannot be later than End datetime")
        
        self.__start_datetime = start_datetime
    
    def set_end_datetime(self, end_datetime):
        if isinstance(end_datetime, str):
            end_datetime = datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M:%S")

        if end_datetime < self.get_start_datetime():
            raise ValueError("End datetime cannot be later than Start datetime")
        
        self.__end_datetime = end_datetime
    
    def add_section(self, section):
        if section in self.__section_list:
            raise ValueError(str(section)+" section already exists")

        self.__section_list.append(str(section))
    
    def enrol_learner(self, staff_id):
        if len(self.__learners_enrolled) == self.get_class_size():
            raise ValueError("Class is full")

        if staff_id in self.__learners_enrolled:
            raise ValueError("Staff "+ str(staff_id)+" already enrolled")

        self.__learners_enrolled.append(str(staff_id))
    
    def remove_section(self, section):
        self.__section_list.remove(str(section))
    
    def json(self):
        return {
            "course_id": self.get_course_id(),
            "class_id": self.get_class_id(),
            "start_datetime": self.get_start_datetime().isoformat(),
            "end_datetime": self.get_end_datetime().isoformat(),
            "class_size": self.get_class_size(),
            "trainer_assigned": self.get_trainer_assigned(),
            "learners_enrolled": self.get_learners_enrolled(),
            "section_list": self.get_section_list(),
        }

class ClassDAO:
    def __init__(self):
        self.table = session.resource('dynamodb', region_name='ap-southeast-1').Table('Class')

    #Create
    def insert_class(self, course_id, class_id, start_datetime, end_datetime, class_size, trainer_assigned = None, learners_enrolled= [], section_list=[]):
        if(isinstance(start_datetime, datetime)):
            start_datetime = start_datetime.isoformat()

        if(isinstance(end_datetime, datetime)):
            end_datetime = end_datetime.isoformat()

        try:
            response = self.table.put_item(
                Item = {
                    "class_id": class_id,
                    "start_datetime": start_datetime,
                    'end_datetime' : end_datetime,
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
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Class already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))
    
    def insert_class_w_dict(self, class_dict):
        if(isinstance(class_dict['start_datetime'], datetime)):
            class_dict['start_datetime'] = class_dict['start_datetime'].isoformat()

        if(isinstance(class_dict['end_datetime'], datetime)):
            class_dict['end_datetime'] = class_dict['end_datetime'].isoformat()

        if 'trainer_assigned' not in class_dict:
            class_dict['trainer_assigned'] = None
        
        if 'learners_enrolled' not in class_dict:
            class_dict['learners_enrolled'] = []
        
        if 'section_list' not in class_dict:
            class_dict['section_list'] = []

        try:
            response = self.table.put_item(
                Item = {
                    "class_id": class_dict['class_id'],
                    "start_datetime": class_dict['start_datetime'],
                    'end_datetime' : class_dict['end_datetime'],
                    'class_size': class_dict['class_size'],
                    'trainer_assigned': class_dict['trainer_assigned'],
                    'learners_enrolled': class_dict['learners_enrolled'],
                    "section_list": class_dict['section_list'],
                    "course_id": class_dict['course_id']
                },
                ConditionExpression=Attr("course_id").not_exists() & Attr('class_id').not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Class(class_dict)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Class already exists")
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

        return [Class(item) for item in response['Items']]
    
    def retrieve_one(self, course_id, class_id):
        response = self.table.get_item(Key={'course_id': course_id, 'class_id': class_id})
        
        if 'Item' in response:
            return Class(response['Item'])
        
        return
    

    def retrieve_all_from_course(self, course_id):
        response = self.table.query(KeyConditionExpression=Key('course_id').eq(course_id))
    
        return [Class(item) for item in response['Items']]


    def retrieve_trainer_classes(self, course_id, staff_id):
        class_list= self.retrieve_all_from_course(course_id)

        if class_list==[]:
            raise ValueError('No classes found for the given course_id ' + course_id)

        returned_list=[]
        for each_class in class_list:
            if each_class.get_trainer_assigned() == staff_id:
                returned_list.append(each_class)

        return returned_list
        
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
            raise ValueError('Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
            
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))

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
            raise ValueError('Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise Exception("Delete Failure with Exception: "+str(e))

if __name__ == "__main__":
    dao = ClassDAO()
    # print(dao.retrieve_all())
    # print(dao.insert_class("IS111",2, datetime(2021,9,27,8,0,0), datetime(2021,10,27,8,0,0), 40))
    # class1 = dao.retrieve_all()[0]
    # print(dao.delete_class(class1))
    # print(class1.json())
    # class1.set_start_datetime(datetime(2021,9,28,16,0,0))
    # print(class1.get_start_datetime())
    # print(dao.update_class(class1))
    # print(dao.retrieve_one("IS111",1))