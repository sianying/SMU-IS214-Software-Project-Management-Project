# Name: Sian Ying

import unittest
import boto3
import sys
sys.path.append('../')
from uuid import uuid4
from moto import mock_dynamodb2

PROGRESS1 = {
            "staff_id": "851252d7-b21c-4d75-95b6-321471ba3910",
            "course_id": "IC112",
            "class_id": 1,
            "final_quiz_passed": True,
            "sections_completed": ["0a08ff5c-d72a-4207-b1de-9bbe99efa7fd", "e565b935-2adc-43b2-9d1c-c8fc29eee91a"]          
}

PROGRESS2 = {
            "staff_id": "657452d7-b21c-4d75-95b6-784251ba3910",
            "course_id": "IC112",
            "class_id": 1,
            "final_quiz_passed": False,
            "sections_completed": ["0a08ff5c-d72a-4207-b1de-9bbe99efa7fd"]          
}

PROGRESS3 = {
            "staff_id": "634289d9-b21c-4d75-95b6-770427ba3854",
            "course_id": "IC112",
            "class_id": 1,
            "final_quiz_passed": False,
            "sections_completed": ["0a08ff5c-d72a-4207-b1de-9bbe99efa7fd"]      
}

PROGRESS4 = {
            "staff_id": "273819d9-b21c-4d75-95b6-770427ba3824",
            "course_id": "IC114",
            "class_id": 1,
            "final_quiz_passed": False,
            "sections_completed": []         
}

class TestProgress(unittest.TestCase):
    def setUp(self):
        from modules.progress_manager import Progress
        self.test_progress = Progress(PROGRESS1)

    def tearDown(self):
        self.test_progress = None

    def test_json(self):
        self.assertTrue(isinstance(self.test_progress.json(), dict), "Progress JSON is not a dictionary object")
        self.assertNotEqual(PROGRESS3, self.test_progress.json(), "Progress matched when it should not")
        self.assertEqual(PROGRESS1, self.test_progress.json(), "Progress does not match")

    def test_set_final_quiz_passed(self):
        self.test_progress.set_final_quiz_passed(False)
        self.assertEqual(self.test_progress.get_final_quiz_passed(), False, "Final quiz status did not update properly")
    
    def test_add_completed_section(self):
        to_add = str(uuid4())
        self.test_progress.add_completed_section(to_add)
        self.assertEqual(to_add, self.test_progress.get_sections_completed()[-1], "Completed section does not match after adding")

@mock_dynamodb2
class TestProgressDAO(unittest.TestCase):

    def setUp(self):
        from modules import create_tables
        from modules.progress_manager import ProgressDAO
        self.dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-1")
        results = create_tables.create_progress_table(self.dynamodb)
        self.table = self.dynamodb.Table('Progress')
        self.table.put_item(Item = PROGRESS1)
        self.dao = ProgressDAO()

    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb = None

    def test_insert_progress(self):
        from modules.progress_manager import Progress
        insertDefault = self.dao.insert_progress(PROGRESS2)
        self.assertTrue(isinstance(insertDefault, Progress))

        insertTest = self.dao.insert_progress(PROGRESS3)

        self.assertEqual(PROGRESS3, insertTest.json(), "ProgressDAO insert failure")
        with self.assertRaises(ValueError, msg = "Failed to prevent duplicate insert") as context:
            self.dao.insert_progress(PROGRESS2)

        self.assertTrue("Progress already exists" == str(context.exception))

    def test_retrieve_by_learner_and_course(self):
        progressObj = self.dao.retrieve_by_learner_and_course("851252d7-b21c-4d75-95b6-321471ba3910", "IC112")
        self.assertEqual(PROGRESS1, progressObj.json(), "Retrieved progress does not match")

        progressObj2 = self.dao.retrieve_by_learner_and_course("273819d9-b21c-4d75-95b6-770427ba3824", "IC114")
        self.assertEqual(None, progressObj2, "Retrieved progress when it should not")

    def test_update_progress(self):
        from modules.progress_manager import Progress
        progressObj = Progress(PROGRESS1)
        progressObj.add_completed_section(str(uuid4()))
        progressObj.set_final_quiz_passed(False)
        self.dao.update_progress(progressObj)

        toCheck = self.table.get_item(Key={'staff_id': progressObj.get_staff_id(), 'course_id': progressObj.get_course_id()})['Item']
        self.assertEqual(progressObj.json(), toCheck, "SectionDAO update test failure")

if __name__ == "__main__":
    unittest.main()