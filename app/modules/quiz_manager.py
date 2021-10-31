import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import copy
from uuid import uuid4

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")

class Question:
    def __init__(self, *args):
        '''
            __init__(
                question_no: integer,
                isMCQ: boolean,
                question_name: String,
                options: List
                correct_option: Integer
                marks: Integer
            )

            __init__(question_dict)
        '''

        if len(args)> 1:
            self.__question_no = int(args[0])
            self.__isMCQ = args[1]
            self.__question_name = args[2]
            self.__options = args[3]
            self.__correct_option = int(args[4])
            self.__marks = int(args[5])
        elif isinstance(args[0], dict):
            self.__question_no = int(args[0]['question_no'])
            self.__isMCQ = args[0]['isMCQ']
            self.__question_name = args[0]['question_name']
            self.__options = args[0]['options']
            self.__correct_option = int(args[0]['correct_option'])
            self.__marks = int(args[0]['marks'])

    def get_question_no(self):
        return self.__question_no

    def isMCQ(self):
        return self.__isMCQ

    def get_question_name(self):
        return self.__question_name

    def get_options(self):
        return self.__options
    
    def get_correct_option(self):
        return self.__correct_option
    
    def get_marks(self):
        return self.__marks

    def json(self):
        return {
            "question_no": self.get_question_no(),
            "isMCQ": self.isMCQ(),
            "question_name": self.get_question_name(),
            "options": self.get_options(),
            "correct_option": self.get_correct_option(),
            "marks": self.get_marks()
        }


class Quiz:
    def __init__(self, *args, **kwargs):
        '''
            __init__(
                quiz_id: string,
                section_id: string,
                time_limit: int,
                questions = []: List
            )

            __init__(quiz_dict)
        '''

        if len(args) > 1:
            self.__section_id=args[0]
            self.__quiz_id = args[1]
            self.__time_limit = int(args[2])

            try:
                self.__questions = [Question(ques_dict) for ques_dict in kwargs['questions']]
            except:
                self.__questions = []
            

        elif isinstance(args[0], dict):
            self.__section_id= args[0]['section_id']
            self.__quiz_id = args[0]['quiz_id']
            self.__time_limit = int(args[0]['time_limit'])
            self.__questions = [Question(ques_dict) for ques_dict in args[0]['questions']]
        
    def get_quiz_id(self):
        return self.__quiz_id
    
    def get_section_id(self):
        return self.__section_id

    def get_time_limit(self):
        return self.__time_limit

    def get_questions(self):
        return self.__questions
    
    def add_question(self, question):
        if not isinstance(question, Question):
            raise ValueError('Object added is not a Question Object')
        self.__questions.append(question)
    
    def remove_question(self, question_index):
        self.__questions.pop(question_index)

    def json(self):
        return {
            "section_id": self.get_section_id(),
            "quiz_id": self.get_quiz_id(),
            "time_limit": self.get_time_limit(),
            "questions": [question.json() for question in self.get_questions()]
        }

class QuizDAO:
    def __init__(self):
        self.table = session.resource('dynamodb',region_name='ap-southeast-1').Table('Quiz')

    #Create
    def insert_quiz(self, section_id, time_limit, quiz_id = None, questions= []):
        try:
            if quiz_id == None:
                quiz_id = str(uuid4())
            response = self.table.put_item(
                Item = {
                    "section_id": section_id,
                    "quiz_id": quiz_id,
                    "time_limit": time_limit,
                    "questions": questions
                },
                ConditionExpression=Attr("quiz_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Quiz(section_id, quiz_id, time_limit, questions=questions)
            return 'Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            return "Quiz already exists"
        except Exception as e:
            return "Insert Failure with Exception: "+str(e)
    
    def insert_quiz_w_dict(self, quiz_dict):
        try:
            if 'questions' not in quiz_dict:
                quiz_dict['questions'] = []

            if 'quiz_id' not in quiz_dict:
                quiz_dict['quiz_id'] = str(uuid4())

            response = self.table.put_item(
                Item = {
                    "quiz_id": quiz_dict['quiz_id'],
                    "section_id": quiz_dict['section_id'],
                    "time_limit": quiz_dict['time_limit'],
                    "questions": quiz_dict['questions']
                },
                ConditionExpression=Attr("section_id").not_exists(),
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Quiz(quiz_dict)
            raise ValueError('Insert Failure with quiz_id: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Quiz already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))


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
        response = self.table.query(IndexName = "SectionIndex", KeyConditionExpression=Key('section_id').eq(section_id))
        
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
                UpdateExpression= "set time_limit = :t, questions = :q",
                ExpressionAttributeValues ={
                    ":t": QuizObj.get_time_limit(),
                    ":q": [question.json() for question in QuizObj.get_questions()],
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
