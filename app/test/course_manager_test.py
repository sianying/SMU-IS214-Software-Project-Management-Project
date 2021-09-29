import unittest
import boto3
import sys
sys.path.append('../')
from decimal import Decimal
from moto import mock_dynamodb2
from modules.course_manager import Course

ITEM1= {
    "course_id": "IS111",
    "course_name": "Intro to Programming",
    "prerequisite_course": ["IS110", "IS113","IS114"],
    "class_list": [Decimal('1'),Decimal('2')]
}

ITEM2 = {
    "course_id": "IS110",
    "course_name": "Test Course",
    "prerequisite_course": [],
    "class_list": []
}

ITEM3 = {
    "course_id": "IS113",
    "course_name": "Test Course 2",
    "prerequisite_course": [],
    "class_list": []
}

@mock_dynamodb2
class TestCourseDAO(unittest.TestCase):

    def setUp(self):
        from modules import create_tables
        from modules.course_manager import CourseDAO 
        self.dynamodb = boto3.resource('dynamodb')
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
        insertTest = self.dao.insert_course(ITEM3['course_id'], ITEM3['course_name'], ITEM3['class_list'], ITEM3['prerequisite_course']).json()
        duplicateTest = self.dao.insert_course(ITEM3['course_id'], ITEM3['course_name'], ITEM3['class_list'], ITEM3['prerequisite_course'])

        self.assertEqual(ITEM3, insertTest, "CourseDAO insert test failure")
        self.assertEqual("Course already exists", duplicateTest, "CourseDAO insert duplicate test failure")

    def test_retrieve_all(self):
        course_list = self.dao.retrieve_all()
        self.assertEqual([ITEM1, ITEM2], [course.json() for course in course_list])

    def test_retrieve_one(self):
        self.assertEqual(ITEM1, self.dao.retrieve_one(ITEM1['course_id']).json(), "CourseDAO retrieve existing one test failure")
        self.assertEqual(None, self.dao.retrieve_one("abcdea"), "CourseDAO retrieve not existing one test failure")

    def test_update_course(self):
        courseObj = Course(ITEM1)
        courseObj.add_class(Decimal('3'))
        courseObj.add_prerequisite_course("IS211")
        self.dao.update_course(courseObj)
        toCheck = self.table.get_item(Key={'course_id':courseObj.get_course_id(), 'course_name':courseObj.get_course_name()})['Item']
        self.assertEqual(courseObj.json(), toCheck, "CourseDAO update test failure")

    def test_delete_course(self):
        courseObj = Course(ITEM2)
        self.dao.delete_course(courseObj)
        key = {'course_id':courseObj.get_course_id(), 'course_name': courseObj.get_course_name()}
        with self.assertRaises(Exception, msg="CourseDAO delete test failure"):
            self.table.get_item(Key = key)['Item']


if __name__ == "__main__":
    unittest.main()