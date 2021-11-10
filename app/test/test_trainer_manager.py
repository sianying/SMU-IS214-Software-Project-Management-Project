#Name: Lee Zong Han

import unittest
import boto3
import sys
sys.path.append('../')
from uuid import uuid4
from moto import mock_dynamodb2
from unittest.mock import patch

#ported over these test cases from test_staff_manager

ITEM1 = {
    "staff_id": "851252d7-b21c-4d75-95b6-321471ba3910",
    "staff_name": "George",
    "role": "Engineer",
    "isTrainer": True,
    "courses_completed": ["IS110", "IS113"],
    "courses_enrolled": ['IS112'],
    "courses_can_teach": ['IS115', 'IS130'],
    "courses_teaching": ['IS115']
}

ITEM2 = {
    "staff_id": "851252d7-b21c-4d75-95b6-321471baasde",
    "staff_name": "Tom",
    "role": "Engineer",
    'isTrainer': True, 
    "courses_completed": [],
    "courses_enrolled": [],
    "courses_can_teach": ['IS120', 'IS220'],
    'courses_teaching': ['IS120']
}

ITEM3 = {
    "staff_id": "123456d7-b12c-3d45-67b8-654321baasde",
    "staff_name": "Tom",
    "role": "Engineer",
    "isTrainer": True,
    "courses_completed": [],
    "courses_enrolled": [],
    "courses_can_teach":[],
    "courses_teaching":[]
}

class TestTrainer(unittest.TestCase):
    def setUp(self):
        from modules.trainer_manager import Trainer
        self.test_trainer = Trainer(ITEM1)

    def tearDown(self):
        self.test_trainer = None
    
    def test_json(self):
        self.assertTrue(isinstance(self.test_trainer.json(), dict), "Trainer JSON is not a dictionary object")
        self.assertEqual(ITEM1, self.test_trainer.json(), "Trainer does not match")
        self.assertNotEqual(ITEM2, self.test_trainer.json(), "Trainer matched when it should not")

    def test_add_can_teach(self):
        self.test_trainer.add_can_teach("IS116")
        self.assertEqual(["IS115", "IS130", "IS116"], self.test_trainer.get_courses_can_teach(), "Failed to add a teachable course.")
        
        with self.assertRaises(ValueError, msg="Failed to raise exception when adding duplicate") as context:
            self.test_trainer.add_can_teach("IS115")
        
        self.assertTrue("IS115 has already been recorded as a teachable course." == str(context.exception))

    def test_remove_can_teach(self):
        self.test_trainer.remove_can_teach("IS115")
        self.assertEqual(["IS130"], self.test_trainer.get_courses_can_teach(), "Failed to remove a teachable course.")

        with self.assertRaises(ValueError, msg="Able to remove a course that doesn't exist"):
            self.test_trainer.remove_can_teach("IS21321")

    def test_add_course_teaching(self):
        with self.assertRaises(ValueError, msg="Can add a course that Trainer is not qualified to teach") as context:
            self.test_trainer.add_course_teaching("IS450")
        self.assertTrue("The trainer is currently not qualified to teach IS450" == str(context.exception))

        with self.assertRaises(ValueError, msg="IS115 is already taught by the trainer currently.") as context:
            self.test_trainer.add_course_teaching("IS115")
        self.assertTrue("IS115 is already taught by the trainer currently." == str(context.exception))

        self.test_trainer.add_course_teaching("IS130")
        self.assertEqual(["IS115", "IS130"], self.test_trainer.get_courses_teaching(), "Failed to add a course that the trainer is teaching.")

    def test_remove_course_teaching(self):
        self.test_trainer.remove_course_teaching("IS115")
        self.assertEqual([], self.test_trainer.get_courses_teaching(), "Failed to remove a course that trainer is teaching")

        with self.assertRaises(ValueError, msg="Able to remove a course that doesn't exist"):
            self.test_trainer.remove_course_teaching("IS21321")


@mock_dynamodb2
class TestTrainerDAO(unittest.TestCase):
    def setUp(self):
        from modules import create_tables
        from modules.trainer_manager import TrainerDAO
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
        results = create_tables.create_staff_table(self.dynamodb)
        self.table = self.dynamodb.Table('Staff')
        self.table.put_item(Item= ITEM1)
        self.table.put_item(Item= ITEM2)
        self.dao = TrainerDAO()

    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb = None

    def test_insert_trainer_w_dict(self):
        from modules.trainer_manager import Trainer
        insertDefault = self.dao.insert_trainer_w_dict({"staff_name": "abcde", "role":"HR"})
        self.assertTrue(isinstance(insertDefault, Trainer))

        insertTest = self.dao.insert_trainer_w_dict(ITEM3)
        self.assertEqual(ITEM3, insertTest.json(), "TrainerDAO insert test failure")

        with self.assertRaises(ValueError, msg = "Failed to raise exception for duplicates") as context:
            self.dao.insert_trainer_w_dict(ITEM2)

        self.assertTrue("Trainer already exists" == str(context.exception))

    def test_retrieve_all(self):
        trainer_list = self.dao.retrieve_all()
        self.assertEqual([ITEM1, ITEM2], [trainerObj.json() for trainerObj in trainer_list])

    def test_retrieve_one(self):
        self.assertEqual(ITEM1, self.dao.retrieve_one(ITEM1['staff_id']).json(), "TrainerDAO retrieve existing one test failure")
        self.assertEqual(None, self.dao.retrieve_one("abcdea"), "TrainerDAO retrieved non-existent trainer, test failure")

    def test_retrieve_qualified_trainers(self):
        trainer_can_teach = self.dao.retrieve_qualified_trainers("IS120")
        self.assertEqual([ITEM2], [trainerObj.json() for trainerObj in trainer_can_teach], "TrainerDAO did not retrieve correct trainer who can teach IS120.")

        none_can_teach = self.dao.retrieve_qualified_trainers("IS13437346743")
        self.assertEqual([], [trainerObj2.json() for trainerObj2 in none_can_teach], "Should have returned empty list.")

    def test_retrieve_courses_teaching(self):
        course_list=self.dao.retrieve_courses_teaching(ITEM2['staff_id'])
        self.assertEqual(['IS120'], course_list, "TrainerDAO did not retrieve the correct list of courses")

        with self.assertRaises(ValueError, msg = "TrainerDAO returned something even when staff_id does not exist") as context:
            self.dao.retrieve_courses_teaching('fake_staff_id')

        self.assertTrue("No trainer found for the given staff id." == str(context.exception))

    def test_update_trainer(self):
        from modules.trainer_manager import Trainer
        trainerObj = Trainer(ITEM1)
        trainerObj.add_can_teach("IS114")
        trainerObj.add_course_teaching("IS130")
        self.dao.update_trainer(trainerObj)
        toCheck = self.table.get_item(Key={'staff_id': trainerObj.get_staff_id(), "staff_name": trainerObj.get_staff_name()})['Item']
        self.assertEqual(trainerObj.json(), toCheck, "TrainerDAO updated values do not match")


if __name__ == "__main__":
    unittest.main()