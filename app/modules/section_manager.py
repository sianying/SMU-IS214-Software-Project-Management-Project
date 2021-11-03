import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")


class Section:
    def __init__(self, section_dict):
        '''
        __init__(section_dict)
        section_dict = {
            section_id: String,
            section_name: String,
            course_id: String,
            class_id: Integer,
            section_number: Integer,
            materials = []: List
            quiz = None: String
        }
        '''

        self.__section_id = section_dict['section_id']
        self.__section_name = section_dict["section_name"]
        self.__course_id = section_dict["course_id"]
        self.__class_id = int(section_dict["class_id"])
        self.__section_number = int(section_dict['section_number'])
        self.__materials = [Material(mat_dict) for mat_dict in section_dict["materials"]] if 'materials' in section_dict else []
        self.__quiz = section_dict["quiz"] if 'quiz' in section_dict else None

    #Getters
    def get_section_id(self):
        return self.__section_id
    
    def get_section_name(self):
        return self.__section_name
    
    def get_course_id(self):
        return self.__course_id
    
    def get_class_id(self):
        return self.__class_id
    
    def get_materials(self):
        return self.__materials
    
    def get_quiz(self):
        return self.__quiz
    
    def get_section_number(self):
        return self.__section_number

    #Setters
    def add_quiz(self, quiz):
        self.__quiz = quiz
    
    def add_material(self, material):
        if not isinstance(material, Material):
            raise ValueError('Object added is not a Material Object')

        self.__materials.append(material)

    def remove_material(self, material_index):
        self.__materials.pop(material_index)

    def json(self):
        return {
            "section_id": self.get_section_id(),
            "section_name": self.get_section_name(),
            "course_id": self.get_course_id(),
            "class_id": self.get_class_id(),
            "section_number": self.get_section_number(),
            "materials": [mat.json() for mat in self.get_materials()],
            "quiz": self.get_quiz()
        }

class Material:
    def __init__(self, mat_dict):
        '''
            __init__(material_dict)
            material_dict ={
                mat_name: String
                mat_type: String
                url: String
            }
        '''
        self.__mat_name = mat_dict['mat_name']
        self.__mat_type = mat_dict['mat_type']
        self.__url = mat_dict['url']
    
    def get_mat_name(self):
        return self.__mat_name
    
    def get_mat_type(self):
        return self.__mat_type
    
    def get_url(self):
        return self.__url

    def json(self):
        return {
            "mat_name": self.get_mat_name(),
            "mat_type": self.get_mat_type(),
            "url": self.get_url()
        }

class SectionDAO:
    def __init__(self):
        self.table = session.resource('dynamodb', region_name='ap-southeast-1').Table('Section')
    
    #Create
    def insert_section_w_dict(self, section_dict): 
        try: 
            if 'section_id' not in section_dict:
                section_dict['section_id'] = str(uuid4())

            if 'materials' not in section_dict:
                section_dict['materials'] = []

            if 'quiz' not in section_dict:
                section_dict['quiz'] = None

            if 'section_number' not in section_dict:
                # retrieve all from class and get the next index
                section_list = self.retrieve_all_from_class(section_dict['course_id'], section_dict['class_id'])
                section_dict['section_number'] = len(section_list)+1

            response = self.table.put_item(
                Item = {
                    "section_id": section_dict['section_id'],
                    "section_name": section_dict['section_name'],
                    "course_id": section_dict['course_id'],
                    "class_id": section_dict['class_id'],
                    'section_number': section_dict['section_number'],
                    "materials": section_dict['materials'],
                    "quiz": section_dict['quiz']
                },
                ConditionExpression=Attr("section_id").not_exists(),
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Section(section_dict)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Section already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))

    #Read
    def retrieve_all_from_class(self, course_id, class_id):
        # retrieve all items and add them to a list of Course objects
        response = self.table.query(IndexName="CourseIndex", KeyConditionExpression=Key('course_id').eq(course_id) & Key('class_id').eq(class_id))

        section_list = sorted(response['Items'], key= lambda x: int(x['section_number']))

        return [Section(section) for section in section_list]

    def retrieve_one(self, section_id):
        response = self.table.query(KeyConditionExpression=Key('section_id').eq(section_id))
        
        if response['Items'] == []:
            return 
        
        return Section(response['Items'][0])

    #Update
    def update_section(self, sectionObj):
        # method updates the DB if there is new prereq course, removing of prereq course, adding new class
        # assumes course_id and course_name cannot be updated
        try:
            response = self.table.update_item(
                Key = {
                    'section_id': sectionObj.get_section_id(),
                    'class_id': sectionObj.get_class_id()
                },
                UpdateExpression= "set quiz = :q, materials = :m",
                ExpressionAttributeValues ={
                    ":q": sectionObj.get_quiz(),
                    ':m': [mat.json() for mat in sectionObj.get_materials()]
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Section Updated'
            raise ValueError('Update Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
            
        except Exception as e:
            raise Exception("Update Failure with Exception: "+str(e))
