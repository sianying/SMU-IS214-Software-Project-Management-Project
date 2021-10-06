import unittest
import boto3
import sys
sys.path.append('../')
from uuid import uuid4
from moto import mock_dynamodb2
from unittest.mock import patch

ITEM1 = {
    "staff_id": "851252d7-b21c-4d75-95b6-321471ba3910",
    "staff_name": "George",
    "courses_completed": ["IS110", "IS113"],
    "courses_enrolled": ['IS112'],
    "role": "Engineer"
}

ITEM2 = {
    "staff_id": "851252d7-b21c-4d75-95b6-321471baasde",
    "staff_name": "Tom",
    "courses_completed": [],
    "courses_enrolled": [],
    "role": "HR"
}

ITEM3 = {
    "staff_id": "851252d7-b21c-4d75-95b6-321471baefg",
    "staff_name": "Tom",
    "courses_completed": [],
    "courses_enrolled": [],
    "role": "HR"
}

IS111 = {
    "course_id": "IS111",
    "course_name": "Intro to Programming",
    "course_description": "lorem ipsum",
    "prerequisite_course": ["IS110", "IS113","IS114"],
    "class_list": [1, 2]
}


class TestStaff(unittest.TestCase):
    def setUp(self):
        from modules.staff_manager import Staff
        self.test_staff = Staff(ITEM1)

    def tearDown(self):
        self.test_staff = None
    
    def test_json(self):
        self.assertTrue(isinstance(self.test_staff.json(), dict), "Staff JSON is not a dictionary object")
        self.assertEqual(ITEM1, self.test_staff.json(), "Staff does not match")
        self.assertNotEqual(ITEM2, self.test_staff.json(), "Staff matched when it should not")
    
    def test_add_completed(self):
        self.test_staff.add_completed("IS114")
        self.assertEqual(["IS110", "IS113", "IS114"], self.test_staff.get_courses_completed(), "Failed to add completed course")
        
        with self.assertRaises(ValueError, msg="Failed to raise exception when adding duplicate") as context:
            self.test_staff.add_completed("IS110")
        
        self.assertTrue("IS110 already completed" == str(context.exception))
    
    def test_add_enrolled(self):
        self.test_staff.add_enrolled("IS114")
        self.assertEqual(["IS112","IS114"], self.test_staff.get_courses_enrolled(), "Failed to add enrolled course")
        
        with self.assertRaises(ValueError, msg="Failed to raise exception when adding duplicate") as context:
            self.test_staff.add_enrolled("IS112")
        
        self.assertTrue("Already enrolled in IS112" == str(context.exception))

    def test_remove_enrolled(self):
        self.test_staff.remove_enrolled("IS112")
        self.assertEqual([], self.test_staff.get_courses_enrolled(), "Failed to remove enrolled course")

        with self.assertRaises(ValueError, msg="Able to remove a course that doesn't exist"):
            self.test_staff.remove_enrolled("IS21321")


@mock_dynamodb2
class TestStaffDAO(unittest.TestCase):
    def setUp(self):
        from modules import create_tables
        from modules.staff_manager import StaffDAO
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        results = create_tables.create_staff_table(self.dynamodb)
        self.table = self.dynamodb.Table('Staff')
        self.table.put_item(Item= ITEM1)
        self.table.put_item(Item= ITEM2)
        self.dao = StaffDAO()
    
    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb = None

    def test_insert_staff(self):
        from modules.staff_manager import Staff
        insertDefault = self.dao.insert_staff("abcde", "HR")
        self.assertTrue(isinstance(insertDefault, Staff))

        insertTest = self.dao.insert_staff(ITEM3['staff_name'], ITEM3['role'], ITEM3['staff_id'], ITEM3['courses_completed'], ITEM3['courses_enrolled'])

        self.assertEqual(ITEM3, insertTest.json(), "StaffDAO insert test failure")

        with self.assertRaises(ValueError, msg = "Failed to raise exception for duplicates") as context:
            self.dao.insert_staff(ITEM2['staff_name'], ITEM2['role'], ITEM2['staff_id'], ITEM2['courses_completed'], ITEM2['courses_enrolled'])

        self.assertTrue("Staff already exists" == str(context.exception))

    def test_insert_staff_w_dict(self):
        from modules.staff_manager import Staff
        insertDefault = self.dao.insert_staff_w_dict({"staff_name": "abcde", "role":"HR"})
        self.assertTrue(isinstance(insertDefault, Staff))

        insertTest = self.dao.insert_staff_w_dict(ITEM3)

        self.assertEqual(ITEM3, insertTest.json(), "StaffDAO insert test failure")

        with self.assertRaises(ValueError, msg = "Failed to raise exception for duplicates") as context:
            self.dao.insert_staff_w_dict(ITEM2)

        self.assertTrue("Staff already exists" == str(context.exception))

    def test_retrieve_all(self):
        staff_list = self.dao.retrieve_all()
        self.assertEqual([ITEM1, ITEM2], [staffObj.json() for staffObj in staff_list])

    def test_retrieve_one(self):
        self.assertEqual(ITEM1, self.dao.retrieve_one(ITEM1['staff_id']).json(), "StaffDAO retrieve existing one test failure")
        self.assertEqual(None, self.dao.retrieve_one("abcdea"), "StaffDAO retrieve not existing one test failure")

    def test_update_staff(self):
        from modules.staff_manager import Staff
        staffObj = Staff(ITEM1)
        staffObj.add_completed("IS114")
        staffObj.add_enrolled("IS115")
        self.dao.update_staff(staffObj)
        toCheck = self.table.get_item(Key={'staff_id': staffObj.get_staff_id(), "staff_name": staffObj.get_staff_name()})['Item']
        self.assertEqual(staffObj.json(), toCheck, "StaffDAO updated values does not match")

    def test_delete_staff(self):
        from modules.staff_manager import Staff
        staffObj = Staff(ITEM2)
        self.dao.delete_staff(staffObj)
        key = {'staff_id': staffObj.get_staff_id(), 'staff_name': staffObj.get_staff_name()}
        with self.assertRaises(Exception, msg = 'StaffDAO delete test failure'):
            self.table.get_item(Key = key)['Item']
    
    @patch("modules.staff_manager.CourseDAO")
    def test_retrieve_all_courses_enrolled(self, mock_course_dao):
        mock_course_dao().retrieve_all_in_list.return_value = [IS111]
        course_list = self.dao.retrieve_all_courses_enrolled(ITEM1["staff_id"])
        self.assertEqual([IS111], course_list)

    @patch("modules.staff_manager.CourseDAO")
    def test_retrieve_all_eligible_to_enroll(self, mock_course_dao):
        mock_course_dao().retrieve_eligible_course.return_value = [IS111]
        course_list = self.dao.retrieve_all_eligible_to_enroll(ITEM1["staff_id"])
        self.assertEqual([IS111], course_list)

if __name__ == "__main__":
    unittest.main()