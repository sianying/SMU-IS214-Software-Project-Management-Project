#Name: Sim Jing Wei   SMU ID: 01357888

import unittest
import boto3
import sys
sys.path.append('../')
from uuid import uuid4
from moto import mock_dynamodb2

ATTEMPT1 = {
    "quiz_id": "4301fff4-6adb-4bd4-b995-40fcf6a4b4ee",
    "staff_id": "aae3e316-af31-40ae-9540-0e3a401b20f6",
    "attempt_id": 1,
    "overall_score": 0,
    "attempt_uuid": "23d98d98-6dcc-4001-996b-c555fe919cfd",
    "options_selected": [1, 0],
    "individual_scores": [0, 0]
}

ATTEMPT2 = {
    "quiz_id": "4301fff4-6adb-4bd4-b995-40fcf6a4b4ee",
    "staff_id": "bae3e316-af31-40ae-9540-0e3a401b20f6",
    "attempt_id": 2,
    "overall_score": 1,
    "attempt_uuid": "3e30a53e-6b42-4f52-a554-58e8d315e838",
    "options_selected": [0, 0],
    "individual_scores": [1, 0]
}

ATTEMPT3 = {
    "quiz_id": "03947jjj1-7adb-9bd4-n695-70cdf67a83hh",
    "staff_id": "aae3e316-af31-40ae-9540-0e3a401b20f6",
    "attempt_id": 2,
    "overall_score": 1,
    "attempt_uuid": "3e30a53e-6b42-4f52-a554-58e245h4fh2",
    "options_selected": [0, 0],
    "individual_scores": [1, 0]
}

class TestAttempt(unittest.TestCase):
    def setUp(self):
        from modules.attempt_manager import Attempt
        self.test_attempt = Attempt(ATTEMPT1)

    def tearDown(self):
        self.test_attempt = None

    def test_json(self):
        self.assertTrue(isinstance(self.test_attempt.json(), dict), "Attempt JSON is not a dictionary object")
        self.assertEqual(ATTEMPT1, self.test_attempt.json(), "Attempt does not match")
        self.assertNotEqual(ATTEMPT2, self.test_attempt.json(), "Attempt matched when it should not")


@mock_dynamodb2
class TestAttemptDAO(unittest.TestCase):
    def setUp(self):
        from modules import create_tables
        from modules.attempt_manager import AttemptDAO
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
        results = create_tables.create_attempt_table(self.dynamodb)
        self.table = self.dynamodb.Table('Attempt')
        self.table.put_item(Item = ATTEMPT1)
        self.table.put_item(Item = ATTEMPT2)
        self.dao = AttemptDAO()
    
    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb = None

    def test_insert_attempt(self):
        from modules.attempt_manager import Attempt
        insertTest = self.dao.insert_attempt(ATTEMPT3, [0,1], [1,1])
        #checks if insertTest is an instance of Attempt class
        self.assertTrue(isinstance(insertTest, Attempt), "AttemptDAO insert is not an instance of Attempt")
        #checks if AttemptDAO inserts input object correctly
        self.assertEqual(ATTEMPT3, insertTest.json(), "AttemptDAO insert is different from input Attempt")
        #checks if an exception is raised if a duplicate Attempt is inserted
        with self.assertRaises(ValueError, msg = "Failed to raise exception for duplicates") as context:
            self.dao.insert_attempt(ATTEMPT2, [0,1], [1,1])
        
        self.assertTrue("Attempt already exists" == str(context.exception))

    def test_retrieve_by_quiz(self):
        #retrieves a list of Attempts of a quiz that exists in the database (by quiz id)
        attempt_list = self.dao.retrieve_by_quiz("4301fff4-6adb-4bd4-b995-40fcf6a4b4ee")
        #retrieves a list of Attempts of a quiz that does not exists in the database (by quiz id)
        attempt_list2 = self.dao.retrieve_by_quiz("abc123")
        #checks if all Attempts of a quiz are retrieved
        self.assertEqual([ATTEMPT1, ATTEMPT2], [attemptObj.json() for attemptObj in attempt_list], "Failed to retrieve all attempts for a quiz")
        #checks if returned list of Attempts are sorted by attempt_uuid
        self.assertNotEqual([ATTEMPT2, ATTEMPT1], [attemptObj.json() for attemptObj in attempt_list], "Retrieve attempts for a quiz is not sorted")
        #checks if an empty list if returned for a quiz that does not exists
        self.assertEqual([], [attemptObj.json() for attemptObj in attempt_list2], "Retrieved objects when nothing should be retrieved")

    def test_retrieve_by_learner(self):
        #retrieves a list of Attempts of a quiz, specific to a learner using quiz_id and staff_id
        attempt_list = self.dao.retrieve_by_learner("4301fff4-6adb-4bd4-b995-40fcf6a4b4ee", "aae3e316-af31-40ae-9540-0e3a401b20f6")
        #retrieves a list of Attempts of a quiz for a learner who does not exists 
        attempt_list2 = self.dao.retrieve_by_learner("4301fff4-6adb-4bd4-b995-40fcf6a4b4ee", "12313")
        #retrieves a list of Attempts of a quiz that does not exists
        attempt_list3 = self.dao.retrieve_by_learner("123123", "aae3e316-af31-40ae-9540-0e3a401b20f6")
        #checks if all Attempts of a quiz of a specific learner is retrieved
        self.assertEqual([ATTEMPT1], [attemptObj.json() for attemptObj in attempt_list], "Failed to retrieve all attempts for a quiz of a specific learner")
        #checks if no Attempts are retrieved for an unregistered learner
        self.assertEqual([], [attemptObj.json() for attemptObj in attempt_list2], "Retrieved objects when nothing should be retrieved")
        #checks if no Attempts are retrieevd for a quiz that does not exists
        self.assertEqual([], [attemptObj.json() for attemptObj in attempt_list3], "Retrieved objects when nothing should be retrieved")



if __name__ == "__main__":
    unittest.main()