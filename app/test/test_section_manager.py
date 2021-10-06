import unittest
import boto3
import sys
sys.path.append('../')
from uuid import uuid4
from moto import mock_dynamodb2

MATERIAL1 = {
    "mat_name": "Paper Feeder Chapter 1",
    "mat_type": "doc",
    "url" : "www.s3bucket.com"
}

MATERIAL2 = {
    "mat_name": "Paper Feeder Chapter 2",
    "mat_type": "doc",
    "url" : "www.s3bucket.com"
}


SECTION1 = {
    "section_id": "0a08ff5c-d72a-4207-b1de-9bbe99efa7fd",
    "section_name": "Paper Feeder",
    "course_id": "IS111",
    "class_id": 1,
    "materials": [MATERIAL1],
    "quiz": "e565b935-2adc-43b2-9d1c-c8fc29eee91a"
}

SECTION2 = {
    "section_id": "0a08ff5c-d72a-4207-b1de-9bbe99easdsd",
    "section_name": "Ink",
    "course_id": "IS111",
    "class_id": 1,
    "materials": [],
    "quiz": None
}

SECTION3 = {
    "section_id": "0a08ff5c-d72a-4207-b1de-9bbe99eaaadsd",
    "section_name": "Ink2",
    "course_id": "IS110",
    "class_id": 1,
    "materials": [],
    "quiz": None
}

class TestMaterial(unittest.TestCase):
    def setUp(self):
        from modules.section_manager import Material
        self.test_material = Material(MATERIAL1)

    def tearDown(self):
        self.test_material = None
    
    def test_json(self):
        self.assertTrue(isinstance(self.test_material.json(), dict), "Material JSON is not a dictionary")
        self.assertEqual(MATERIAL1, self.test_material.json(), "Material JSON does not match")
        self.assertNotEqual(MATERIAL2, self.test_material.json(), "Material JSON matched when it should not")

class TestSection(unittest.TestCase):
    def setUp(self):
        from modules.section_manager import Section
        self.test_section = Section(SECTION1)
    
    def tearDown(self):
        self.test_section = None
    
    def test_json(self):
        self.assertTrue(isinstance(self.test_section.json(), dict), "Section JSON is not a dictionary object")
        self.assertEqual(SECTION1, self.test_section.json(), "Section JSON does not match")
        self.assertNotEqual(SECTION2, self.test_section.json(), "Section JSON matched when it should not")
    
    def test_add_quiz(self):
        to_add = uuid4()
        self.test_section.add_quiz(to_add)
        self.assertEqual(to_add, self.test_section.get_quiz(), "Quiz does not match after adding")
        
    def test_add_material(self):
        from modules.section_manager import Material
        self.test_section.add_material(Material(MATERIAL2))
        self.assertEqual([MATERIAL1, MATERIAL2], [mat.json() for mat in self.test_section.get_materials()], "Material list does not match after adding material")

        with self.assertRaises(ValueError, msg="Failed to raise exception when adding a non-material object") as context:
            self.test_section.add_material(MATERIAL2)
        
        self.assertTrue("Object added is not a Material Object" == str(context.exception))
    
    def test_remove_material(self):
        with self.assertRaises(IndexError, msg="Failed to raise exception when index out of range") as context:
            self.test_section.remove_material(1)

        self.assertTrue("pop index out of range" == str(context.exception))
        self.test_section.remove_material(0)
        self.assertEqual([], self.test_section.get_materials())

@mock_dynamodb2
class TestSectionDAO(unittest.TestCase):
    def setUp(self):
        from modules import create_tables
        from modules.section_manager import SectionDAO
        self.dynamodb = boto3.resource('dynamodb', region_name = 'ap-southeast-1')
        results = create_tables.create_section_table(self.dynamodb)
        self.table=self.dynamodb.Table('Section')
        self.table.put_item(Item = SECTION1)
        self.table.put_item(Item = SECTION2)
        self.dao = SectionDAO()

    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb= None
    
    def test_insert_section(self):
        from modules.section_manager import Section
        insertDefault = self.dao.insert_section("abcd","efgh",1)
        self.assertTrue(isinstance(insertDefault, Section))

        insertTest = self.dao.insert_section(SECTION3['section_name'], SECTION3['course_id'], SECTION3['class_id'], SECTION3['section_id'], SECTION3['materials'], SECTION3['quiz'])

        self.assertEqual(SECTION3, insertTest.json(), "SectionDAO inserted values do not match")

        with self.assertRaises(ValueError, msg ="Failed to prevent duplicate insert") as context:
            self.dao.insert_section(SECTION1['section_name'], SECTION1['course_id'], SECTION1['class_id'], SECTION1['section_id'], SECTION1['materials'], SECTION1['quiz'])
        
        self.assertTrue("Section already exists" == str(context.exception))
    
    def test_insert_section_w_dict(self):
        from modules.section_manager import Section
        insertDefault = self.dao.insert_section_w_dict({"section_name": 'abdce', 'course_id':'abcde', 'class_id':1})
        self.assertTrue(isinstance(insertDefault, Section))


        insertTest = self.dao.insert_section_w_dict(SECTION3)

        self.assertEqual(SECTION3, insertTest.json(), "SectionDAO dictionary insert values do not match")

        with self.assertRaises(ValueError, msg ="Failed to prevent duplicate insert") as context:
            self.dao.insert_section_w_dict(SECTION1)
        
        self.assertTrue("Section already exists" == str(context.exception))

    def test_retrieve_all_from_class(self):
        section_list = self.dao.retrieve_all_from_class("IS111", 1)
        self.assertEqual([SECTION1, SECTION2], [section.json() for section in section_list], msg="Retrieved sections from class does not match")

        section_list2 = self.dao.retrieve_all_from_class("IS110",2)
        self.assertEqual([], [section.json() for section in section_list2], msg="Retrieved sections when it should not retrieve anything")
    
    def test_retrieve_one(self):
        self.assertEqual(SECTION1, self.dao.retrieve_one(SECTION1['section_id']).json(), "SectionDAO retrieve existing one test failure")
        self.assertEqual(None, self.dao.retrieve_one("abcdea"), "SectionDAO retrieve not existing one test failure")

    def test_update_section(self):
        from modules.section_manager import Section, Material
        sectionObj = Section(SECTION2)
        sectionObj.add_material(Material(MATERIAL1))
        sectionObj.add_quiz(str(uuid4()))
        self.dao.update_section(sectionObj)
        toCheck = self.table.get_item(Key={'section_id': sectionObj.get_section_id(), 'class_id': sectionObj.get_class_id()})['Item']
        self.assertEqual(sectionObj.json(), toCheck, "SectionDAO update test failure")

    def test_delete_course(self):
        from modules.section_manager import Section
        sectionObj = Section(SECTION2)
        self.dao.delete_section(sectionObj)
        key = {'section_id':sectionObj.get_section_id(), 'class_id': sectionObj.get_class_id()}
        with self.assertRaises(Exception, msg="SectionDAO delete test failure"):
            self.table.get_item(Key = key)['Item']

if __name__ == "__main__":
    unittest.main()