import boto3
import os
from boto3.dynamodb.conditions import Key
from uuid import uuid4

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")


class Progress:
    def __init__(self, *args, **kwargs):
        '''
            __init__(
                course_id: string,
                class_id: int,
                staff_id: string,
                final_quiz_passed: boolean, 
                sections_completed = []: List
            )

            __init__(attempt_dict)
        '''

        if len(args) > 1:
            self.__course_id = args[0]
            self.__class_id = args[1]
            self.__staff_id = args[2]
            self.__final_quiz_passed = args[3] 

            try:
                self.__sections_completed = kwargs['sections_completed']
            except:
                self.__sections_completed = []


        elif isinstance(args[0], dict):
            self.__course_id= args[0]['course_id']
            self.__class_id= args[0]['class_id']
            self.__staff_id = args[0]['staff_id']
            self.__final_quiz_passed = args[0]['final_quiz_passed']
            self.__sections_completed = args[0]['sections_completed']
        
    def get_course_id(self):
        return self.__course_id
    
    def get_class_id(self):
        return self.__class_id

    def get_staff_id(self):
        return self.__staff_id

    def get_final_quiz_passed(self):
        return self.__final_quiz_passed

    def get_sections_completed(self):
        return self.__sections_completed

    def set_final_quiz_passed(self, final_quiz_passed):
        self.__final_quiz_passed = final_quiz_passed

    def add_completed_section(self, section_uuid):
        self.__sections_completed.append(section_uuid)

    def json(self):
        return {
            "quiz_id": self.get_quiz_id(),
            "class_id": self.get_class_id(),
            "staff_id": self.get_staff_id(),
            "final_quiz_passed": self.get_final_quiz_passed(),
            "sections_completed": self.get_sections_completed()           
        }


class ProgressDAO:
    def __init__(self):
        self.table = session.resource('dynamodb', region_name = "ap-southeast-1").Table('Progress')

    #Create
    def insert_progress(self, progress_dict):
        try:
            attempt_list = self.retrieve_by_learner(progress_dict['quiz_id'], attempt_dict['staff_id'])

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
    #for the trainer to see his entire section's scores
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
