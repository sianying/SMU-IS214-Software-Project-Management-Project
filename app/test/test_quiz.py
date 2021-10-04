import unittest
import boto3
import sys
sys.path.append('../')
from moto import mock_dynamodb2
from modules.quiz_manager import Quiz

ITEM1= {
    "section_id": "s1",
    "quiz_id": "q1",
    "questions": [
        {
            "question_no": 1,
            "isMCQ": False,
            "question_name": "Is this true?",
            "options":["True", "False"],
            "correct_option": 1, # 1 refers index 1-> False
            "marks": 1
        },

        {
            "question_no": 2,
            "isMCQ": True,
            "question_name": "How long should you take to complete most jobs?",
            "options":["30 min", "45 min", "1 hour", "1.5 hour"],
            "correct_option": 2, # 2 refers to index 2-> 1 hour
            "marks": 2
        }
    ]

}

ITEM2 = {
    "section_id": "s2",
    "quiz_id": "q2",
    "questions": [
        {
            "question_no": 3,
            "isMCQ": False,
            "question_name": "Are you motivated?",
            "options":["True", "False"],
            "correct_option": 0, #True
            "marks": 1
        },

        {
            "question_no": 4,
            "isMCQ": True,
            "question_name": "How many days do you work per week",
            "options":["4 days", "5 days", "6 days", "7 days"],
            "correct_option": 1, #5 days
            "marks": 2
        }
    ]
}

ITEM3 = {
    "section_id": "s3",
    "quiz_id": "q3",
    "questions": [
        {
            "question_no": 5,
            "isMCQ": False,
            "question_name": "You enjoyed studying the material provided.",
            "options":["True", "False"],
            "correct_option": 0, #True
            "marks": 3
        },
    ]
}

@mock_dynamodb2
class TestQuizDAO(unittest.TestCase):

    def setUp(self):
        from modules import create_tables
        from modules.quiz_manager import QuizDAO 
        self.dynamodb = boto3.resource('dynamodb')
        results = create_tables.create_quiz_table(self.dynamodb)
        #print(results)
        self.table = self.dynamodb.Table('Quiz')
        self.table.put_item(Item = ITEM1)
        self.table.put_item(Item = ITEM2)
        self.dao = QuizDAO()

    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb = None

    def test_insert_Quiz(self):
        insertTest = self.dao.insert_quiz(ITEM3['section_id'], ITEM3['quiz_id'], ITEM3['questions']).json()
        duplicateTest = self.dao.insert_quiz(ITEM3['section_id'], ITEM3['quiz_id'], ITEM3['questions'])

        self.assertEqual(ITEM3, insertTest, "QuizDAO insert test failure")
        self.assertEqual("Quiz already exists", duplicateTest, "QuizDAO insert duplicate test failure")


    def test_retrieve_all(self):
        quiz_list = self.dao.retrieve_all()
        self.assertEqual(len(quiz_list), 2, "QuizDAO did not retrieve the correct number of records(2).")


    def test_retrieve_one(self):
        self.assertEqual(ITEM1, self.dao.retrieve_one(ITEM1['quiz_id']).json(), "QuizDAO did not retrieve the correct quiz by quiz_id, test failure")
        self.assertEqual(None, self.dao.retrieve_one("fakequizid"), "QuizDAO should have returned nothing, test failure (quiz_id)")


    def test_retrieve_by_section(self):
        self.assertEqual(ITEM2, self.dao.retrieve_by_section(ITEM2['section_id']).json(), "QuizDAO did not retrieve the correct quiz by section_id, test failure")
        self.assertEqual(None, self.dao.retrieve_by_section("fakesection"), "QuizDAO should have returned nothing, test failure (section_id)")


    def test_update_quiz(self):
        quizObj = Quiz(ITEM1)
        question= {
            "question_no": 6,
            "isMCQ": True,
            "question_name": "Should you arrive on time to work?",
            "options":["True", "False"],
            "correct_option": 0, #Index 0-> True
            "marks": 1
        }
        quizObj.add_question(question)
        self.dao.update_quiz(quizObj)
        toCheck = self.table.get_item(Key={'quiz_id':quizObj.get_quiz_id(), 'section_id':quizObj.get_section_id()})['Item']
        self.assertEqual(quizObj.json(), toCheck, "QuizDAO update test failure")


    def test_delete_quiz(self):
        quizObj = Quiz(ITEM2)
        self.dao.delete_quiz(quizObj)
        key = {'quiz_id':quizObj.get_quiz_id(), 'section_id': quizObj.get_section_id()}
        with self.assertRaises(Exception, msg="QuizDAO did not delete quiz, test failure"):
            self.table.get_item(Key = key)['Item']


if __name__ == "__main__":
    unittest.main()