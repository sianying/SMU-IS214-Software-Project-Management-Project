import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = "../aws_credentials"

class Quiz:
    def __init__(self, *args, **kwargs):
        '''
            __init__(
                quiz_id: int,
                section_id: int
                questions = []: List
            )

            __init__(quiz_dict)
        '''

        if len(args) > 1:
            self.__quiz_id = args[0]
            self.__section_id=args[1]

            try:
                self.__questions = kwargs['questions']
            except:
                self.__questions = []
            

        elif isinstance(args[0], dict):
            self.__quiz_id = args[0]['quiz_id']
            self.__section_id= args[0]['section_id']
            self.__questions = args[0]['questions']
        
    def get_quiz_id(self):
        return self.__quiz_id
    
    def get_section_id(self):
        return self.__section_id

    def get_questions(self):
        return self.__questions
    
    def add_questions(self, question):
        self.__questions.append(question)
    
    def remove_question(self, question):
        self.__courses_enrolled.remove(question)


class QuizDAO:
    def __init__(self):
        self.table = boto3.resource('dynamodb').Table('Quiz')

    #Create
    def insert_quiz(self, section_id, quiz_id = None, questions= []):
        try:
            if quiz_id == None:
                quiz_id = str(uuid4())
            response = self.table.put_item(
                Item = {
                    "quiz_id": quiz_id,
                    "section_id": section_id,
                    "questions": questions
                },
                ConditionExpression=Attr("quiz_id").not_exists()
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Quiz(quiz_id, questions=questions)
            return 'Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode'])
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            return "Quiz Already Exists"
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
    def delete_Quiz(self, QuizObj):
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




    # print(dao.retrieve_all())
    # print(dao.insert_staff("Johnny", "HR"))
    # print(dao.insert_staff("Tom", "Engineer"))
    # staff1 = dao.retrieve_all()[1]
    # print(staff1.get_staff_id())
    # print(dao.delete_staff(staff1))
    # tom = dao.retrieve_one("6724873a-b951-4ee7-a835-cb0f9f784c45")
    # tom.add_completed("IS110")
    # tom.add_enrolled("IS111")
    # print(dao.update_staff(johnny))
    # print(tom.get_courses_enrolled())
    # print(tom.get_courses_completed())

    # for staff in dao.retrieve_all():
    #     print(staff.get_staff_id())