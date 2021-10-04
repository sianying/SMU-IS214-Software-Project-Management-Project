import unittest
import boto3
import sys
import os
sys.path.append('../')
from decimal import Decimal
from moto import mock_dynamodb2

ITEM1= {
    "course_id": "IS111",
    "course_name": "Intro to Programming",
    "course_description": "lorem ipsum",
    "prerequisite_course": ["IS110", "IS113","IS114"],
    "class_list": [1, 2]
}

ITEM2 = {
    "course_id": "IS110",
    "course_name": "Test Course",
    "course_description": "lorem_ipsum",
    "prerequisite_course": [],
    "class_list": []
}

ITEM3 = {
    "course_id": "IS113",
    "course_name": "Test Course 2",
    "course_description": "lorem ipsum",
    "prerequisite_course": [],
    "class_list": []
}

class TestCourse(unittest.TestCase):
    def setUp(self):
        from modules.course_manager import Course
        self.test_course = Course(ITEM1)
    
    def tearDown(self):
        self.test_course = None

    def test_json(self):
        self.assertEqual(ITEM1, self.test_course.json(), "Course does not match")
        self.assertNotEqual(ITEM2, self.test_course.json(), "Course matched when it should not")

    def test_add_class(self):
        self.test_course.add_class(3)
        self.assertEqual(ITEM1["class_list"] + [3], self.test_course.get_class_list(), "Class list does not match after adding class")
    
    def test_add_prerequisite_course(self):
        self.test_course.add_prerequisite_course("IS112")
        self.assertEqual(ITEM1["prerequisite_course"] + ["IS112"], self.test_course.get_prerequisite_course(), "Prerequisite does not match after adding prerequisite course")
        

@mock_dynamodb2
class TestCourseDAO(unittest.TestCase):

    def setUp(self):
        from modules import create_tables
        from modules.course_manager import CourseDAO 
        self.dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        results = create_tables.create_course_table(self.dynamodb)
        # print(results)
        self.table = self.dynamodb.Table('Course')
        self.table.put_item(Item = ITEM1)
        self.table.put_item(Item = ITEM2)
        self.dao = CourseDAO()

    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb = None

    def test_insert_course(self):
        insertTest = self.dao.insert_course(ITEM3['course_id'], ITEM3['course_name'], ITEM3['course_description'], ITEM3['class_list'], ITEM3['prerequisite_course']).json()

        self.assertEqual(ITEM3, insertTest, "CourseDAO insert test failure")
        with self.assertRaises(ValueError, msg = "Failed to prevent duplicate insert") as context:
            self.dao.insert_course(ITEM2['course_id'], ITEM2['course_name'], ITEM2['course_description'], ITEM2['class_list'], ITEM2['prerequisite_course'])

        self.assertTrue("Course already exists" == str(context.exception))

    def test_retrieve_all(self):
        course_list = self.dao.retrieve_all()
        self.assertEqual([ITEM1, ITEM2], [course.json() for course in course_list])

    def test_retrieve_one(self):
        self.assertEqual(ITEM1, self.dao.retrieve_one(ITEM1['course_id']).json(), "CourseDAO retrieve existing one test failure")
        self.assertEqual(None, self.dao.retrieve_one("abcdea"), "CourseDAO retrieve not existing one test failure")

    def test_update_course(self):
        from modules.course_manager import Course
        courseObj = Course(ITEM1)
        courseObj.add_class(Decimal('3'))
        courseObj.add_prerequisite_course("IS211")
        self.dao.update_course(courseObj)
        toCheck = self.table.get_item(Key={'course_id':courseObj.get_course_id(), 'course_name':courseObj.get_course_name()})['Item']
        self.assertEqual(courseObj.json(), toCheck, "CourseDAO update test failure")

    def test_delete_course(self):
        from modules.course_manager import Course
        courseObj = Course(ITEM2)
        self.dao.delete_course(courseObj)
        key = {'course_id':courseObj.get_course_id(), 'course_name': courseObj.get_course_name()}
        with self.assertRaises(Exception, msg="CourseDAO delete test failure"):
            self.table.get_item(Key = key)['Item']


if __name__ == "__main__":
    unittest.main()