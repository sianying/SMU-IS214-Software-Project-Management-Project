import boto3
import os
from boto3.dynamodb.conditions import Key
from uuid import uuid4

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")


class Attempt:
    def __init__(self, *args, **kwargs):
        '''
            __init__(
                quiz_id: string,
                staff_id: string,
                attempt_id: int, 
                overall_score: int,
                attempt_uuid = None: string, 
                options_selected = []: List,
                individual_scores = []: List
            )

            __init__(attempt_dict)
        '''

        if len(args) > 1:
            self.__quiz_id = args[0]
            self.__staff_id = args[1]
            self.__attempt_id = args[2]
            self.__overall_score = args[3] 
            self.__attempt_uuid = args[4]

            try:
                self.__options_selected = kwargs['options_selected']
            except:
                self.__options_selected = []

            try:
                self.__individual_scores = kwargs['individual_scores']
            except:
                self.__individual_scores = []
            

        elif isinstance(args[0], dict):
            self.__quiz_id= args[0]['quiz_id']
            self.__staff_id = args[0]['staff_id']
            self.__attempt_id = args[0]['attempt_id']
            self.__overall_score = args[0]['overall_score']
            self.__attempt_uuid = args[0]['attempt_uuid']
            self.__options_selected = args[0]['options_selected']
            self.__individual_scores = args[0]['individual_scores']
        
    def get_quiz_id(self):
        return self.__quiz_id
    
    def get_staff_id(self):
        return self.__staff_id

    def get_attempt_id(self):
        return self.__attempt_id

    def get_overall_score(self):
        return self.__overall_score

    def get_options_selected(self):
        return self.__options_selected

    def get_individual_scores(self):
        return self.__individual_scores

    def get_attempt_uuid(self):
        return self.__attempt_uuid

    def json(self):
        return {
            "quiz_id": self.get_quiz_id(),
            "staff_id": self.get_staff_id(),
            "attempt_id": self.get_attempt_id(),
            "overall_score": self.get_overall_score(),
            "attempt_uuid": self.get_attempt_uuid(),
            "options_selected": self.get_options_selected(),
            "individual_scores": self.get_individual_scores()
        }


class AttemptDAO:
    def __init__(self):
        self.table = session.resource('dynamodb', region_name = "ap-southeast-1").Table('Attempt')

    #Create
    def insert_attempt(self, attempt_dict, correct_options, marks):
        try:
            attempt_list = self.retrieve_by_learner(attempt_dict['quiz_id'], attempt_dict['staff_id'])

            if 'attempt_id' in attempt_dict and attempt_dict['attempt_id'] in attempt_list:
                raise ValueError('Attempt already exists')

            if 'attempt_id' not in attempt_dict:
                attempt_dict['attempt_id'] = len(attempt_list)+1

            if 'attempt_uuid' not in attempt_dict:
                attempt_dict['attempt_uuid'] = str(uuid4())


            options_selected=attempt_dict['options_selected']
            individual_scores=[]
            #assume that options_selected and correct_options will have same length.
            #frontend should ensure "empty" answers are filled in even when question is not answered.
            for i in range(len(options_selected)):
                if options_selected[i]==correct_options[i]:
                    individual_scores.append(marks[i])
                else:
                    individual_scores.append(0)

            attempt_dict['individual_scores'] = individual_scores
            overall = sum(individual_scores)
            attempt_dict['overall_score'] = overall
            response = self.table.put_item(
                Item = {
                    "staff_id": attempt_dict['staff_id'],
                    "quiz_id": attempt_dict['quiz_id'],
                    "attempt_id": attempt_dict['attempt_id'],
                    "overall_score": attempt_dict['overall_score'],
                    "attempt_uuid": attempt_dict['attempt_uuid'],
                    "options_selected": attempt_dict['options_selected'],
                    "individual_scores": attempt_dict['individual_scores']
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Attempt(attempt_dict)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            print(e)
            raise Exception("Insert Failure with Exception: "+str(e))
    
    #Read
    #to check if any attempts has been made, then cannot update quiz anymore
    def retrieve_by_quiz(self, quiz_id):
        
        # retrieve all items and add them to a list of Attempt objects
        response = self.table.query(KeyConditionExpression=Key('quiz_id').eq(quiz_id))
        data = response['Items']

        attempt_list = []

        for item in data:
            attempt_list.append(Attempt(item))

        return attempt_list


    #for the learner to see different attempts for the same quiz
    def retrieve_by_learner(self, quiz_id, staff_id):

        #retrieve all items for a particular learner for a particular quiz
        response= self.table.query(IndexName="StaffIndex", KeyConditionExpression=Key('quiz_id').eq(quiz_id) & Key('staff_id').eq(staff_id))
        data = response['Items']

        attempts_list = []

        for item in data:
            attempts_list.append(Attempt(item))

        return attempts_list

