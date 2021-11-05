import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")

class Question:
    def __init__(self, question_dict):
        '''
            __init__(question_dict)
            question_dict = {
                question_no: integer,
                isMCQ: boolean,
                question_name: String,
                options: List
                correct_option: Integer
                marks: Integer
            }
        '''
        self.__question_no = int(question_dict['question_no'])
        self.__isMCQ = question_dict['isMCQ']
        self.__question_name = question_dict['question_name']
        self.__options = question_dict['options']
        self.__correct_option = int(question_dict['correct_option'])
        self.__marks = int(question_dict['marks'])

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
    def __init__(self, quiz_dict):
        '''
            __init__(quiz_dict)
            quiz_dict = {
                quiz_id: string,
                section_id: string,
                time_limit: int,
                questions = []: List
                total_marks: int
            }
        '''
        self.__section_id= quiz_dict['section_id']
        self.__quiz_id = quiz_dict['quiz_id']
        self.__time_limit = int(quiz_dict['time_limit'])
        self.__questions = [Question(ques_dict) for ques_dict in quiz_dict['questions']] if 'questions' in quiz_dict else []
        self.__total_marks = int(quiz_dict['total_marks'])
        
    def get_quiz_id(self):
        return self.__quiz_id
    
    def get_section_id(self):
        return self.__section_id

    def get_time_limit(self):
        return self.__time_limit

    def get_questions(self):
        return self.__questions

    def get_total_marks(self):
        return self.__total_marks

    def set_time_limit(self, time_limit):
        self.__time_limit= time_limit

    def set_questions(self, questions):
        question_list = []
        total_marks = 0
        for question in questions:
            question_obj= Question(question)
            question_list.append(question_obj)
            total_marks+= question_obj.get_marks()

        self.__questions = question_list
        self.__total_marks = total_marks

    def json(self):
        return {
            "section_id": self.get_section_id(),
            "quiz_id": self.get_quiz_id(),
            "time_limit": self.get_time_limit(),
            "questions": [question.json() for question in self.get_questions()],
            "total_marks": self.get_total_marks()
        }

class QuizDAO:
    def __init__(self):
        self.table = session.resource('dynamodb',region_name='ap-southeast-1').Table('Quiz')

    #Create
    def insert_quiz_w_dict(self, quiz_dict):
        try:
            if 'questions' not in quiz_dict:
                quiz_dict['questions'] = []

            if 'quiz_id' not in quiz_dict:
                quiz_dict['quiz_id'] = str(uuid4())
                
            if 'total_marks' not in quiz_dict:
                total_marks = 0
                for question in quiz_dict['questions']:
                    total_marks += question['marks']
                quiz_dict['total_marks'] = total_marks

            response = self.table.put_item(
                Item = {
                    "quiz_id": quiz_dict['quiz_id'],
                    "section_id": quiz_dict['section_id'],
                    "time_limit": quiz_dict['time_limit'],
                    "questions": quiz_dict['questions'],
                    "total_marks": quiz_dict['total_marks']
                },
                ConditionExpression=Attr("quiz_id").not_exists(),
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Quiz(quiz_dict)
            raise ValueError('Insert Failure with quiz_id: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Quiz already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))

    #Read    
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
        # method updates the DB if one wants to set new questions/delete old questions.
        # total_score is recalculated too
        # assumes quiz_id and section_id cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'quiz_id': QuizObj.get_quiz_id(),
                    'section_id': QuizObj.get_section_id()
                },
                UpdateExpression= "set time_limit = :t, questions = :q, total_marks = :m",
                ExpressionAttributeValues ={
                    ":t": QuizObj.get_time_limit(),
                    ":q": [question.json() for question in QuizObj.get_questions()],
                    ":m": QuizObj.get_total_marks(),
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Quiz Updated'
            raise ValueError('Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))

