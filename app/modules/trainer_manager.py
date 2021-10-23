import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import copy
from uuid import uuid4
from modules.staff_manager import Staff

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = "../aws_credentials"

class Trainer(Staff):
    def __init__(self, courses_can_teach, courses_teaching, *args, **kwargs):
        '''
            __init__(
                ------Inherited from Staff-----
                staff_id: int,
                staff_name: String,
                role: String,
                isTrainer: Boolean (always 1)
                courses_completed = []: List,
                courses_enrolled = []: List

                --------Trainer Only----------
                courses_can_teach = []: List
                courses_teaching = []: List
            )

            __init__(staff_dict)
        '''

        super().__init__(*args, **kwargs)
        try:
            self.__courses_can_teach = copy.deepcopy(courses_can_teach)
        except:
            self.__courses_can_teach = []

        try: 
            self.__courses_teaching = copy.deepcopy(courses_teaching)
        except:
            self.__courses_teaching=[]

    # --------------Methods inherited from Staff-----------
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
            "staff_id": self.get_staff_id(),
            "staff_name": self.get_staff_name(),
            "role": self.get_role(),
            "isTrainer": self.get_isTrainer(),
            "courses_completed": self.get_courses_completed(),
            "courses_enrolled": self.get_courses_enrolled(),
            "courses_can_teach": self.get_courses_can_teach(),
            "courses_teaching": self.get_courses_teaching()
        }


def prepare_dict(dict):
    temp=dict.copy()
    temp.pop('courses_can_teach')
    temp.pop('courses_teaching')
    return temp

class TrainerDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb', region_name="ap-southeast-1").Table('Staff')

    #Create
    def insert_trainer(self, staff_name, role, isTrainer=1, staff_id = None, courses_completed= [], courses_enrolled = [], courses_can_teach=[], courses_teaching=[]):
        try:
            if staff_id == None:
                staff_id = str(uuid4())
            response = self.table.put_item(
                Item = {
                    "staff_id": staff_id,
                    "staff_name": staff_name,
                    'role' : role,
                    'isTrainer': isTrainer,
                    'courses_completed': courses_completed,
                    'courses_enrolled': courses_enrolled,
                    'courses_can_teach': courses_can_teach,
                    'courses_teaching': courses_teaching
                },
                ConditionExpression=Attr("staff_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Trainer(courses_can_teach, courses_teaching, staff_id, staff_name, role, isTrainer, courses_completed=courses_completed, courses_enrolled=courses_enrolled)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Trainer already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))
    
    def insert_trainer_w_dict(self, trainer_dict):
        try:
            if 'staff_id' not in trainer_dict or trainer_dict['staff_id'] == None:
                trainer_dict['staff_id'] = str(uuid4())

            if 'isTrainer' not in trainer_dict:
                trainer_dict['isTrainer']=1
            
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
                temp=prepare_dict(trainer_dict)
                return Trainer(trainer_dict['courses_can_teach'], trainer_dict['courses_teaching'], temp)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Trainer already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: " + str(e))


    #Read
    def retrieve_all(self):
        # retrieve all items and add them to a list of trainer objects
        response = self.table.scan(FilterExpression= Key('isTrainer').eq(1))
        data = response['Items']
        # response = self.table.query(KeyConditionExpression = Key('isTrainer').eq(1))

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], FilterExpression= Key('isTrainer').eq(1))
            data.extend(response['Items'])

        trainer_list = []

        for item in data:
            temp = prepare_dict(item)
            trainer_list.append(Trainer(item['courses_can_teach'], item['courses_teaching'], temp))

        return trainer_list
    

    def retrieve_one(self, staff_id):
        response = self.table.scan(FilterExpression = Key('staff_id').eq(staff_id) & Key('isTrainer').eq(1))
        # response = self.table.query(KeyConditionExpression=Key('staff_id').eq(staff_id) & Key('isTrainer').eq("1"))
        
        if response['Items'] == []:
            return 
        
        trainer = response['Items'][0]
        temp = prepare_dict(trainer)

        return Trainer(trainer['courses_can_teach'], trainer['courses_teaching'], temp)


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


    def retrieve_eligible_trainer_to_enrol(self, courseObj):
        trainer_list = self.retrieve_all()
        prereq_course = courseObj.get_prerequisite_course()
        course_id_to_enroll = courseObj.get_course_id()

        result_list = []
        for trainer in trainer_list:
            if trainer.can_enrol(course_id_to_enroll, prereq_course):
                result_list.append(trainer)
        
        return result_list

    #Update
    def update_trainer(self, trainerObj):
        # method updates the DB if there is new prereq course, removing of prereq course, adding new class
        # assumes staff_id, staff_name and role cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'staff_id': trainerObj.get_staff_id(),
                    'staff_name': trainerObj.get_staff_name(),
                    'role': trainerObj.get_role(),
                    'isTrainer': trainerObj.get_isTrainer()
                },
                UpdateExpression= "set courses_completed = :c, courses_enrolled = :e, courses_can_teach = :t, courses_teaching = :x",
                ExpressionAttributeValues ={
                    ":c": trainerObj.get_courses_completed(),
                    ':e': trainerObj.get_courses_enrolled(),
                    ':t': trainerObj.get_courses_can_teach(),
                    ':x': trainerObj.get_courses_teaching()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Trainer Updated'
            raise ValueError('Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
            
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))



    #Delete
    def delete_trainer(self, trainerObj):
        try:
            response = self.table.delete_item(
                Key = {
                    'staff_id': trainerObj.get_staff_id(),
                    'staff_name': trainerObj.get_staff_name()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Trainer Deleted'
            raise ValueError('Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise ValueError("Delete Failure with Exception: "+str(e))