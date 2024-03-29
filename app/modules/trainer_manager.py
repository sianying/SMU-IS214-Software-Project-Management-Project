import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import copy
from uuid import uuid4
from modules.staff_manager import Staff

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = "../aws_credentials"

class Trainer(Staff):
    def __init__(self, staff_dict):
        '''
            __init__(staff_dict)
            staff_dict = {
                ------Inherited from Staff-----
                staff_id: int,
                staff_name: String,
                role: String,
                isTrainer: Boolean (always True)
                courses_completed = []: List,
                courses_enrolled = []: List

                --------Trainer Only----------
                courses_can_teach = []: List
                courses_teaching = []: List
            }
        '''
        super().__init__(staff_dict)
        self.__courses_can_teach = copy.deepcopy(staff_dict['courses_can_teach']) if 'courses_can_teach' in staff_dict else []
        self.__courses_teaching = copy.deepcopy(staff_dict['courses_teaching']) if 'courses_teaching' in staff_dict else []

    # Getter: get_staff_id(), get_staff_name(), get_role(), get_courses_completed(), get_courses_enrolled()
    # Setter: add_completed(course), add_enrolled(course), removed_enrolled(course)
    # Miscellaneous: can_enrol(course_id_to_enrol, prerequisite_list) 

    def get_courses_can_teach(self):
        return self.__courses_can_teach

    def get_courses_teaching(self):
        return self.__courses_teaching

    def add_can_teach(self, course):
        if course in self.__courses_can_teach:
            raise ValueError(str(course) + " has already been recorded as a teachable course.")
        self.__courses_can_teach.append(course)

    def remove_can_teach(self, course):
        self.__courses_can_teach.remove(course)

    def add_course_teaching(self, course):
        if course not in self.__courses_can_teach:
            raise ValueError("The trainer is currently not qualified to teach " + str(course))
        elif course in self.__courses_teaching:
            raise ValueError(str(course) + " is already taught by the trainer currently.")
        self.__courses_teaching.append(course)

    def remove_course_teaching(self, course):
        self.__courses_teaching.remove(course)

    def json(self):
        return {
            **super().json(),
            "courses_can_teach": self.get_courses_can_teach(),
            "courses_teaching": self.get_courses_teaching()
        }

class TrainerDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb', region_name="ap-southeast-1").Table('Staff')

    #Create   
    def insert_trainer_w_dict(self, trainer_dict):
        try:
            if 'staff_id' not in trainer_dict or trainer_dict['staff_id'] == None:
                trainer_dict['staff_id'] = str(uuid4())

            if 'isTrainer' not in trainer_dict:
                trainer_dict['isTrainer']=True
            
            if 'courses_completed' not in trainer_dict:
                trainer_dict['courses_completed'] = []

            if 'courses_enrolled' not in trainer_dict:
                trainer_dict['courses_enrolled'] = []

            if 'courses_can_teach' not in trainer_dict:
                trainer_dict['courses_can_teach'] = []

            if 'courses_teaching' not in trainer_dict:
                trainer_dict['courses_teaching'] = []

            response = self.table.put_item(
                Item = {
                    "staff_id": trainer_dict['staff_id'],
                    "staff_name": trainer_dict['staff_name'],
                    'role' : trainer_dict['role'],
                    'isTrainer': trainer_dict['isTrainer'],
                    'courses_completed': trainer_dict['courses_completed'],
                    'courses_enrolled': trainer_dict['courses_enrolled'],
                    'courses_can_teach': trainer_dict['courses_can_teach'],
                    'courses_teaching': trainer_dict['courses_teaching']
                },
                ConditionExpression=Attr("staff_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Trainer(trainer_dict)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Trainer already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: " + str(e))

    #Read
    def retrieve_all(self):
        # retrieve all items and add them to a list of trainer objects
        response = self.table.scan(FilterExpression= Key('isTrainer').eq(True))
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], FilterExpression= Key('isTrainer').eq(True))
            data.extend(response['Items'])

        trainer_list = []

        for item in data:
            trainer_list.append(Trainer(item))

        return trainer_list
    
    def retrieve_one(self, staff_id):
        response = self.table.scan(FilterExpression = Key('staff_id').eq(staff_id) & Key('isTrainer').eq(True))
        
        if response['Items'] == []:
            return
            
        return Trainer(response['Items'][0])

    def retrieve_qualified_trainers(self, course_id):
        trainer_list = self.retrieve_all()

        returned_list=[]
        for trainer in trainer_list:
            courses_can_teach = trainer.get_courses_can_teach()
            if course_id in courses_can_teach:
                returned_list.append(trainer)

        return returned_list

    def retrieve_courses_teaching(self, staff_id):
        trainer = self.retrieve_one(staff_id)
        
        if trainer==None:
            raise ValueError('No trainer found for the given staff id.')
        return trainer.get_courses_teaching()

    #Update
    def update_trainer(self, trainerObj):
        try:
            response = self.table.update_item(
                Key = {
                    'staff_id': trainerObj.get_staff_id(),
                    'staff_name': trainerObj.get_staff_name(),
                },
                UpdateExpression= "set courses_can_teach = :t, courses_teaching = :x",
                ExpressionAttributeValues ={
                    ':t': trainerObj.get_courses_can_teach(),
                    ':x': trainerObj.get_courses_teaching()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Trainer Updated'
            raise ValueError('Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))