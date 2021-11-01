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
                staff_id: string,
                course_id: string,
                class_id: int,
                final_quiz_passed: boolean, 
                sections_completed = []: List
            )

            __init__(attempt_dict)
        '''

        if len(args) > 1:
            self.__staff_id = args[0]
            self.__course_id = args[1]
            self.__class_id = args[2]
            self.__final_quiz_passed = args[3] 

            try:
                self.__sections_completed = kwargs['sections_completed']
            except:
                self.__sections_completed = []


        elif isinstance(args[0], dict):
            self.__staff_id= args[0]['staff_id']
            self.__course_id= args[0]['course_id']
            self.__class_id = args[0]['class_id']
            self.__final_quiz_passed = args[0]['final_quiz_passed']
            self.__sections_completed = args[0]['sections_completed']

    def get_staff_id(self):
        return self.__staff_id

    def get_course_id(self):
        return self.__course_id
    
    def get_class_id(self):
        return self.__class_id

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
            "staff_id": self.get_staff_id(),
            "course_id": self.get_course_id(),
            "class_id": self.get_class_id(),
            "final_quiz_passed": self.get_final_quiz_passed(),
            "sections_completed": self.get_sections_completed()           
        }


class ProgressDAO:
    def __init__(self):
        self.table = session.resource('dynamodb', region_name = "ap-southeast-1").Table('Progress')

    #Create
    def insert_progress(self, progress_dict):
        try:
            if 'final_quiz_passed' not in progress_dict:
                progress_dict['final_quiz_passed']= False

            if 'sections_completed' not in progress_dict:
                progress_dict['sections_completed']=[]

            response = self.table.put_item(
                Item = {
                    "staff_id": progress_dict['staff_id'],
                    "course_id": progress_dict['course_id'],
                    "class_id": progress_dict['class_id'],
                    "final_quiz_passed": progress_dict['final_quiz_passed'],
                    "sections_completed": progress_dict['sections_completed']
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Progress(progress_dict)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            print(e)
            raise Exception("Insert Failure with Exception: "+str(e))
    
    #Read
    #for the learner to see his progress across all courses
    def retrieve_all_by_learner(self, staff_id):

        # retrieve all items and add them to a list of Progress objects
        response = self.table.scan(FilterExpression = Key('staff_id').eq(staff_id))
        data = response['Items']

        progress_list = []
        for item in data:
            progress_list.append(Progress(item))

        return progress_list


    #for the learner to see his progress for a specific course
    def retrieve_one_by_course(self, staff_id, course_id):

        #retrieve all items for a particular learner for a particular course
        response = self.table.scan(FilterExpression = Key('staff_id').eq(staff_id) & Key('course_id').eq(course_id))
        if response['Items'] == []:
            return 

        return Progress(response['Items'][0])

    #Update
    def update_progress(self, progressObj):
        try:
            response = self.table.update_item(
                Key = {
                    'staff_id': progressObj.get_staff_id(),
                    'course_id': progressObj.get_course_id(),
                    'class_id': progressObj.get_class_id()
                },
                UpdateExpression = "set final_quiz_passed = :f, sections_completed = :s",
                ExpressionAttributeValues ={
                    ':f': progressObj.get_final_quiz_passed(),
                    ':s': progressObj.get_sections_cmmpleted()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Progress Updated'
            raise ValueError('Update Failure with error: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise Exception("Update Failure with Exception: "+ str(e))
