#Name: Lee Yi Hao

import unittest
import boto3
import sys
sys.path.append('../')
from uuid import uuid4
from moto import mock_dynamodb2

ITEM1 = {
    "staff_id": "851252d7-b21c-4d75-95b6-321471ba3910",
    "staff_name": "George",
    "role": "Engineer",
    "isTrainer": 0,
    "courses_completed": ["IS110", "IS113"],
    "courses_enrolled": ['IS112'],
}

ITEM2 = {
    "staff_id": "851252d7-b21c-4d75-95b6-321471baasde",
    "staff_name": "Tom",
    "role": "HR",
    "isTrainer": 0,
    "courses_completed": [],
    "courses_enrolled": [],
}

ITEM3 = {
    "staff_id": "123456d7-b12c-3d45-67b8-654321baasde",
    "staff_name": "Tom",
    "role": "Engineer",
    "isTrainer": 1,
    "courses_completed": [],
    "courses_enrolled": [],
}

IS111 = {
    "course_id": "IS111",
    "course_name": "Intro to Programming",
    "course_description": "lorem ipsum",
    "prerequisite_course": ["IS110", "IS113"],
    "class_list": [1, 2]
}

IS300 = {
    "course_id": "IS300",
    "course_name": "Advanced Programming",
    "course_description": "lorem ipsum",
    "prerequisite_course": [],
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

    def test_convert_trainer(self):
        self.test_staff.convert_trainer()
        trainer_status = self.test_staff.get_isTrainer()
        self.assertEqual(1, trainer_status, "Staff was not successfully converted into trainer.")

        #2nd time, staff is already trainer.
        with self.assertRaises(ValueError, msg="Failed to raise exception when staff is already trainer") as context:
            self.test_staff.convert_trainer()
        
        self.assertTrue("Staff is already a Trainer" == str(context.exception))
    
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

    def test_can_enrol(self):
        self.assertTrue(self.test_staff.can_enrol("IS300", ["IS110"]), "Failed check for enrolment")
        self.assertTrue(self.test_staff.can_enrol("IS300", []), "Failed check for enrolment with no prereq")
        self.assertFalse(self.test_staff.can_enrol("IS300", ["IS700"]), "Failed check not eligible for enrolment")
        self.assertFalse(self.test_staff.can_enrol("IS300", ["IS112"]), "Failed check not eligible for enrolment for enrolled course")


@mock_dynamodb2
class TestStaffDAO(unittest.TestCase):
    def setUp(self):
        from modules import create_tables
        from modules.staff_manager import StaffDAO
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
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

    def test_retrieve_eligible_staff_to_enrol(self):
        from modules.course_manager import Course
        staff_list = self.dao.retrieve_eligible_staff_to_enrol(Course(IS300))
        self.assertEqual([ITEM1, ITEM2], [staff.json() for staff in staff_list], "Eligible staff doesn't match for course with no prerequisite")

        staff_list2 = self.dao.retrieve_eligible_staff_to_enrol(Course(IS111))
        self.assertEqual([ITEM1], [staff.json() for staff in staff_list2], "Eligible staff doesn't match for course with prerequisite")


if __name__ == "__main__":
    unittest.main()