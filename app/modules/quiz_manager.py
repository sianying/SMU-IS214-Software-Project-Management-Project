import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = "../aws_credentials"
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

class Quiz:
    def __init__(self, *args, **kwargs):
        '''
            __init__(
                quiz_id: string,
                section_id: string,
                questions = []: List
            )

            __init__(quiz_dict)
        '''

        if len(args) > 1:
            self.__section_id=args[0]
            self.__quiz_id = args[1]

            try:
                self.__questions = kwargs['questions']
            except:
                self.__questions = []
            

        elif isinstance(args[0], dict):
            self.__section_id= args[0]['section_id']
            self.__quiz_id = args[0]['quiz_id']
            self.__questions = args[0]['questions']
        
    def get_quiz_id(self):
        return self.__quiz_id
    
    def get_section_id(self):
        return self.__section_id

    def get_questions(self):
        return self.__questions
    
    def add_question(self, question):
        self.__questions.append(question)
    
    def remove_question(self, question):
        self.__questions.remove(question)

    def json(self):
        return {
            "section_id": self.get_section_id(),
            "quiz_id": self.get_quiz_id(),
            "questions": self.get_questions()
        }


class QuizDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb', region_name="us-east-1").Table('Quiz')

    #Create
    def insert_quiz(self, section_id, quiz_id = None, questions= []):
        try:
            if quiz_id == None:
                quiz_id = str(uuid4())
            response = self.table.put_item(
                Item = {
                    "section_id": section_id,
                    "quiz_id": quiz_id,
                    "questions": questions
                },
                ConditionExpression=Attr("quiz_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Quiz(section_id, quiz_id, questions=questions)
            return 'Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            return "Quiz already exists"
        except Exception as e:
            return "Insert Failure with Exception: "+str(e)
    
    #Read
    def retrieve_all(self):
        
        # retrieve all items and add them to a list of Quiz objects
        response = self.table.scan()
        data = response['Items']

        # When last evaluated key is present in response it means the results return exceeds the scan limits -> recall scan and explicitly include the key to start at
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])

        quiz_list = []

        for item in data:
            quiz_list.append(Quiz(item))

        return quiz_list
    
    
    def retrieve_one(self, quiz_id):
        response = self.table.query(KeyConditionExpression=Key('quiz_id').eq(quiz_id))
        
        if response['Items'] == []:
            return 
        
        return Quiz(response['Items'][0])


    def retrieve_by_section(self, section_id):
        response = self.table.query(KeyConditionExpression=Key('section_id').eq(section_id))
        
        if response['Items'] == []:
            return 
        
        return Quiz(response['Items'][0])



    #Update
    def update_quiz(self, QuizObj):
        # method updates the DB if one wants to add a new question/delete an existing question.
        # assumes quiz_id cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'quiz_id': QuizObj.get_quiz_id(),
                    'section_id': QuizObj.get_section_id()
                },
                UpdateExpression= "set questions = :q",
                ExpressionAttributeValues ={
                    ":q": QuizObj.get_questions(),
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Quiz Updated'
            return 'Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
            
        except Exception as e:
            return "Update Failure with Exception: "+str(e)

    #Delete
    def delete_quiz(self, QuizObj):
        try:
            response = self.table.delete_item(
                Key = {
                    'quiz_id': QuizObj.get_quiz_id(),
                    'section_id': QuizObj.get_section_id()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Quiz Deleted'
            return 'Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            return "Delete Failure with Exception: "+str(e)

if __name__ == "__main__":
    dao = QuizDAO()
