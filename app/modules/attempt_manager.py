import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = "../aws_credentials"
os.environ['AWS_DEFAULT_REGION'] = 'ap-southeast-1'

class Attempt:
    def __init__(self, *args, **kwargs):
        '''
            __init__(
                quiz_id: string,
                staff_id: string,
                attempt_id: int,  
                options_selected = []: List
            )

            __init__(attempt_dict)
        '''

        if len(args) > 1:
            self.__quiz_id=args[0]
            self.__staff_id = args[1]
            self.__attempt_id: args[2]

            try:
                self.__options_selected = kwargs['options_selected']
            except:
                self.__options_selected = []
            

        elif isinstance(args[0], dict):
            self.__quiz_id= args[0]['quiz_id']
            self.__staff_id = args[0]['staff_id']
            self.__attempt_id = args[0]['attempt_id']
            self.__options_selected = args[0]['options_selected']
        
    def get_quiz_id(self):
        return self.__quiz_id
    
    def get_staff_id(self):
        return self.__staff_id

    def get_attempt_id(self):
        return self.__attempt_id

    def get_options_selected(self):
        return self.__options_selected

    def json(self):
        return {
            "quiz_id": self.get_quiz_id(),
            "staff_id": self.get_staff_id(),
            "attempt_id": self.get_attempt_id(),
            "options_selected": self.get_options_selected()
        }


class AttemptDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb', region_name="ap-southeast-1").Table('Attempt')

    #Create
    def insert_attempt(self, quiz_id, staff_id, attempt_id, options_selected= []):
        try:
            if attempt_id == None:
                attempt_list = self.retrieve_by_learner(quiz_id, staff_id)
                attempt_id = len(attempt_list)+1

            response = self.table.put_item(
                Item = {
                    "staff_id": staff_id,
                    "quiz_id": quiz_id,
                    "attempt_id": attempt_id,
                    "options_selected": options_selected
                },
                ConditionExpression=Attr("quiz_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Attempt(quiz_id, staff_id, attempt_id, options_selected=options_selected)
            return 'Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            return "Attempt already exists"
        except Exception as e:
            return "Insert Failure with Exception: "+str(e)
    
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
        response= self.table.query(KeyConditionExpression=Key('quiz_id').eq(quiz_id) & Key('staff_id').eq(staff_id))
        data = response['Items']

        attempts_list = []

        for item in data:
            attempts_list.append(Attempt(item))

        return attempts_list


    #Update
    def update_quiz(self, AttemptObj):
        # method updates the DB if one wants to add a new question/delete an existing question.
        # assumes quiz_id cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'quiz_id': AttemptObj.get_quiz_id(),
                    'staff_id': AttemptObj.get_staff_id(),
                    'attempt_id': AttemptObj.get_attempt_id()
                },
                UpdateExpression= "set options_selected = :o",
                ExpressionAttributeValues ={
                    ":o": AttemptObj.get_options_selected(),
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Quiz Updated'
            return 'Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
            
        except Exception as e:
            return "Update Failure with Exception: "+str(e)



    #Delete

    #idt should have a delete method, since attempt_id is obtained thru the len(attempts_list) + 1.
    #if delete might result in duplicate attempt_ids
    #doesnt seem to have a need for it too
