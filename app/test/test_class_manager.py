import unittest
import boto3
import sys
sys.path.append('../')
from decimal import Decimal
from moto import mock_dynamodb2
from datetime import datetime
from uuid import uuid4

ITEM1= {
    "course_id": "IS110",
    "class_id": 1,
    "start_datetime": "2021-08-21T08:00:00",
    "end_datetime": "2021-10-21T23:59:59",
    "class_size": 20,
    "trainer_assigned": "851252d7-b21c-4d75-95b6-321471ba3910",
    "final_quiz_id": 'finalquiz1',
    "learners_enrolled": ["2652a20c-999f-485f-9d19-84ce47d7fefa", "b6d178fc-1c54-4d27-bad2-f6f6b75867ab", "115193a6-3d76-4e47-8a69-a9070c6ba96a"],
    "section_list": ["0a08ff5c-d72a-4207-b1de-9bbe99efa7fd"]
}

ITEM2= {
    "course_id": "IS111",
    "class_id": 2,
    "start_datetime": "2021-08-21T08:00:00",
    "end_datetime": "2021-10-21T23:59:59",
    "class_size": 20,
    "trainer_assigned": None,
    "final_quiz_id": None,
    "learners_enrolled": ["2652a20c-999f-485f-9d19-84ce47d7fefa"],
    "section_list": []
}

ITEM3 = {
    "course_id": "IS110",
    "class_id": 3,
    "start_datetime": "2021-08-21T08:00:00",
    "end_datetime": "2021-10-21T23:59:59",
    "class_size": 20,
    "trainer_assigned": 'dummytrainer',
    "final_quiz_id": 'finalquiz3',
    "learners_enrolled": [],
    "section_list": []
}

class TestClass(unittest.TestCase):
    def setUp(self):
        from modules.class_manager import Class
        self.test_class = Class(ITEM1)
        self.test_class2 = Class(ITEM2)

    def tearDown(self):
        del self.test_class 
        del self.test_class2 

    def test_json(self):
        self.assertTrue(isinstance(self.test_class.json(),dict), "Class JSON is not a dictionary object")
        self.assertEqual(ITEM1, self.test_class.json(), "Class does not match")
        self.assertNotEqual(ITEM2, self.test_class.json(), "Class matched when it should not")

    def test_set_class_size(self):
        self.test_class.set_class_size(30)
        self.assertEqual(30, self.test_class.get_class_size(), "Class size set does not match")
        self.test_class.set_class_size(Decimal(40))
        self.assertEqual(40, self.test_class.get_class_size(), "Conversion from Decimal to int failed")

    def test_set_trainer(self):
        self.test_class2.set_trainer('testtrainer')
        self.assertEqual('testtrainer', self.test_class2.get_trainer_assigned(), "Trainer set does not match")

    def test_set_final_quiz_id(self):
        self.test_class2.set_final_quiz_id('testfinalquiz')
        self.assertEqual('testfinalquiz', self.test_class2.get_final_quiz_id(), "Final_quiz_id set does not match")
    
    def test_set_start_datetime(self):
        correct_date = datetime(2021,9,21,8,0,0)
        checker_date = datetime(2021,7,21,8,0,0)
        string_date = "2021-07-21T08:00:00"
        fail_date = datetime(2021,11,21,8,0,0)
        self.test_class.set_start_datetime(correct_date)
        self.assertEqual(correct_date, self.test_class.get_start_datetime(), "(Datetime Object) Start datetime does not match")
        self.assertNotEqual(checker_date, self.test_class.get_start_datetime(), "(Datetime Object) Start datetime matched when it should not")
        
        self.test_class2.set_start_datetime(string_date)
        self.assertEqual(checker_date, self.test_class2.get_start_datetime(), "(String date) Start datetime does not match")
        self.assertEqual(string_date, self.test_class2.get_start_datetime().isoformat(), "(String date)Start datetime isoformat does not match string date")
        self.assertNotEqual(string_date, self.test_class2.get_start_datetime(), "(String date) Start datetime object matches string date when it should not")

        with self.assertRaises(ValueError, msg="Failed to raise exception") as context:
            self.test_class.set_start_datetime(fail_date)

        self.assertTrue("Start datetime cannot be later than End datetime" == str(context.exception))

    def test_set_end_datetime(self):
        correct_date = datetime(2021,11,21,8,0,0)
        checker_date = datetime(2021,12,21,8,0,0)
        string_date = "2021-12-21T08:00:00"
        fail_date = datetime(2021,5,21,8,0,0)
        self.test_class.set_end_datetime(correct_date)
        self.assertEqual(correct_date, self.test_class.get_end_datetime(), "(Datetime Object) End datetime does not match")
        self.assertNotEqual(checker_date, self.test_class.get_end_datetime(), "(Datetime Object) End datetime matched when it should not")
        
        self.test_class2.set_end_datetime(string_date)
        self.assertEqual(checker_date, self.test_class2.get_end_datetime(), "(String date) End datetime does not match")
        self.assertEqual(string_date, self.test_class2.get_end_datetime().isoformat(), "(String date) End datetime isoformat does not match string date")
        self.assertNotEqual(string_date, self.test_class2.get_end_datetime(), "(String date) End datetime object matches string date when it should not")

        with self.assertRaises(ValueError, msg="End datetime failed to raise exception") as context:
            self.test_class.set_end_datetime(fail_date)

        self.assertTrue("End datetime cannot be later than Start datetime" == str(context.exception))

    def test_add_section(self):
        to_add_section_id = str(uuid4())
        duplicate_section_id = "0a08ff5c-d72a-4207-b1de-9bbe99efa7fd"
        self.test_class.add_section(to_add_section_id)
        section_list = self.test_class.get_section_list()

        self.assertTrue(to_add_section_id in section_list, "Failed to add Section UUID into Class")
        
        with self.assertRaises(ValueError, msg="duplicate uuid failed to raise exception") as context:
            self.test_class.add_section(duplicate_section_id)

        self.assertTrue(duplicate_section_id + " section already exists" == str(context.exception))

    def test_enrol_learner(self):
        to_add_staff_id = str(uuid4())
        duplicate_staff_id = "2652a20c-999f-485f-9d19-84ce47d7fefa"
        self.test_class.enrol_learner(to_add_staff_id)
        learners_list = self.test_class.get_learners_enrolled()

        self.assertTrue(to_add_staff_id in learners_list, "Failed to add Learner into Class")

        with self.assertRaises(ValueError, msg="duplicate learners failed to raise exception") as context:
            self.test_class.enrol_learner(duplicate_staff_id)

        self.assertTrue("Staff "+ duplicate_staff_id + " already enrolled" == str(context.exception))

        with self.assertRaises(Exception, msg="full class failed to raise exception") as context2:
            for i in range(self.test_class.get_class_size()):
                self.test_class.enrol_learner(str(uuid4()))

        self.assertTrue("Class is full" == str(context2.exception))

    def test_remove_section(self):
        to_remove = "0a08ff5c-d72a-4207-b1de-9bbe99efa7fd"
        self.test_class.remove_section(to_remove)
        self.assertTrue(to_remove not in self.test_class.get_section_list(), "Failed to remove a section")
        
        with self.assertRaises(ValueError, msg="Able to remove a section that doesn't exist") as context:
            self.test_class.remove_section("abcde")

        self.assertTrue("list.remove(x): x not in list" == str(context.exception))

@mock_dynamodb2
class TestClassDAO(unittest.TestCase):

    def setUp(self):
        from modules import create_tables
        from modules.class_manager import ClassDAO 
        self.dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-1")
        results = create_tables.create_class_table(self.dynamodb)
        # print(results)
        self.table = self.dynamodb.Table('Class')
        self.table.put_item(Item = ITEM1)
        self.table.put_item(Item = ITEM2)
        self.dao = ClassDAO()

    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb = None

    def test_insert_class_w_dict(self):
        from modules.class_manager import Class
        insertDefault = self.dao.insert_class_w_dict({"course_id": "asvde", "class_id":1, "start_datetime": "2021-08-21T08:00:00", "end_datetime":"2021-09-21T08:00:00", "class_size":20})
        self.assertTrue(isinstance(insertDefault, Class))
        insertTest = self.dao.insert_class_w_dict(ITEM3)

        self.assertEqual(ITEM3, insertTest.json(), "ClassDAO insert with dict test failure")

        with self.assertRaises(ValueError, msg = "Failed to raise exception for duplicates") as context:
            self.dao.insert_class_w_dict(ITEM2)
        
        self.assertTrue("Class already exists" == str(context.exception))

    def test_retrieve_one(self):
        self.assertEqual(ITEM1, self.dao.retrieve_one(ITEM1['course_id'], ITEM1['class_id']).json(), "ClassDAO retrieve existing one test failure")
        self.assertEqual(None, self.dao.retrieve_one("abcdea", 2), "ClassDAO retrieve not existing one test failure")

    def test_retrieve_all_from_course(self):
        class_list = self.dao.retrieve_all_from_course("IS110")
        class_list2 = self.dao.retrieve_all_from_course("IS113")
        self.assertEqual([ITEM1], [classObj.json() for classObj in class_list], "Failed to retrieve all classes from a course")
        self.assertEqual([], [classObj.json() for classObj in class_list2], "Retrieved objects when nothing should be retrieved")

    def test_retrieve_trainer_classes(self):
        trainer_classes = self.dao.retrieve_trainer_classes("IS110", '851252d7-b21c-4d75-95b6-321471ba3910')
        trainer_classes2 = self.dao.retrieve_trainer_classes("IS111", 'dummytrainer')

        self.assertEqual([ITEM1], [classObj.json() for classObj in trainer_classes], "Failed to retrieve class that trainer is teaching")
        self.assertEqual([], [classObj.json() for classObj in trainer_classes2], "Retrieved class objects when nothing should be retrieved")

        with self.assertRaises(ValueError, msg = "ClassDAO returned something even when course_id is invalid") as context:
            self.dao.retrieve_trainer_classes('IS42000', '851252d7-b21c-4d75-95b6-321471ba3910')

        self.assertTrue("No classes found for the given course_id IS42000" == str(context.exception))

    def test_update_class(self):
        from modules.class_manager import Class
        classObj = Class(ITEM1)
        classObj.set_class_size(40)
        classObj.enrol_learner(str(uuid4()))
        classObj.add_section(str(uuid4()))
        classObj.remove_section("0a08ff5c-d72a-4207-b1de-9bbe99efa7fd")
        classObj.set_final_quiz_id('newfinalquiz')
        self.dao.update_class(classObj)
        toCheck = self.table.get_item(Key={'course_id':classObj.get_course_id(), 'class_id':classObj.get_class_id()})['Item']
        self.assertEqual(classObj.json(), toCheck, "ClassDAO updated values does not match")


if __name__ == "__main__":
    unittest.main()