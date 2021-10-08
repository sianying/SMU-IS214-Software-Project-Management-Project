import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import copy
from uuid import uuid4

os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "../aws_credentials"

class Section:
    def __init__(self, *args, **kwargs):
        '''__init__(
            section_id: String,
            section_name: String,
            course_id: String,
            class_id: Integer,
            section_number: Integer,
            materials = []: List
            quiz = None: String
        )

        __init__(section_dict)
        '''

        if len(args) > 1:
            self.__section_id = args[0]
            self.__section_name = args[1]
            self.__course_id = args[2]
            self.__class_id = int(args[3])
            self.__section_number = int(args[4])
            try:
                self.__materials = [Material(mat_dict) for mat_dict in kwargs["materials"]]
            except:
                self.__materials = []
            try:
                self.__quiz = kwargs["quiz"]
            except:
                self.__quiz = None
        elif isinstance(args[0], dict):
            self.__section_id = args[0]['section_id']
            self.__section_name = args[0]["section_name"]
            self.__course_id = args[0]["course_id"]
            self.__class_id = int(args[0]["class_id"])
            self.__section_number = int(args[0]['section_number'])
            try:
                self.__materials = [Material(mat_dict) for mat_dict in args[0]["materials"]]
            except:
                self.__materials = []
            try:
                self.__quiz = args[0]["quiz"]
            except:
                self.__quiz = None

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
    def __init__(self, *args):
        '''__init__(
            mat_name: String
            mat_type: String
            url: String
        )

            __init__(material_dict)
        '''
    
        if len(args) > 1:
            self.__mat_name = args[0]
            self.__mat_type = args[1]
            self.__url = args[2]
        elif isinstance(args[0], dict):
            self.__mat_name = args[0]['mat_name']
            self.__mat_type = args[0]['mat_type']
            self.__url = args[0]['url']
    
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
        self.table = boto3.resource('dynamodb', region_name='ap-southeast-1').Table('Section')
    
    #Create
    def insert_section(self, section_name, course_id, class_id, section_number = None, section_id = None, materials = [], quiz = None): 
        try: 
            if section_id == None:
                section_id = str(uuid4())

            if section_number == None:
                # retrieve all from class and get the next index
                section_list = self.retrieve_all_from_class(course_id, class_id)
                section_number = len(section_list)+1

            response = self.table.put_item(
                Item = {
                    "section_id": section_id,
                    "section_name": section_name,
                    "course_id": course_id,
                    "class_id": class_id,
                    "section_number": section_number,
                    "materials": materials,
                    "quiz": quiz
                },
                ConditionExpression=Attr("section_id").not_exists(),
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return Section(section_id, section_name, course_id, class_id, section_number, materials=materials, quiz=quiz)
            raise ValueError('Insert Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as e:
            raise ValueError("Section already exists")
        except Exception as e:
            raise Exception("Insert Failure with Exception: "+str(e))
    
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
            raise ValueError("Update Failure with Exception: "+str(e))

    #Delete
    def delete_section(self, sectionObj):
        try:
            response = self.table.delete_item(
                Key = {
                    'section_id': sectionObj.get_section_id(),
                    'class_id': sectionObj.get_class_id()
                }
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return 'Course Deleted'
            raise ValueError('Delete Failure with code: '+ str(response['ResponseMetadata']['HTTPStatusCode']))
        except Exception as e:
            raise Exception("Delete Failure with Exception: "+str(e))


if __name__ == "__main__":
    dao = SectionDAO()
    
    # section1 = dao.retrieve_one("4b22008c-5d47-426b-aa78-726b528da512")
    # section2 = dao.retrieve_one("367e514e-41a5-4afb-a010-2a1b740069ad")
    # section3 = dao.retrieve_one("33cd4a6e-0a51-4f2c-8014-d8eee1acf6f5")

    # mat1 = Material("Printer Fundamentals Document", "docx", "https://s3.ap-southeast-1.amazonaws.com/spmprojectbucket/PrinterFundamentals.docx")
    # mat2 = Material("Printer Fundamentals Powerpoint", "pptx", "https://s3.ap-southeast-1.amazonaws.com/spmprojectbucket/PrinterFundamentals.pptx")
    # mat3 = Material("Printer Fundamentals PDF", "PDF", "https://s3.ap-southeast-1.amazonaws.com/spmprojectbucket/PrinterFundamentals.pdf")
    
    # section1.add_material(mat1)
    # section2.add_material(mat2)
    # section3.add_material(mat3)

    # dao.update_section(section1)
    # dao.update_section(section2)
    # dao.update_section(section3)