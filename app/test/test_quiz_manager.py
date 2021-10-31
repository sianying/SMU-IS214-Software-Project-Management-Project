import unittest
import boto3
import sys
sys.path.append('../')
from moto import mock_dynamodb2

ITEM1= {
    "section_id": "s1",
    "quiz_id": "q1",
    "time_limit": 3600,
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
    "time_limit": 200,
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

# Final Quiz is not tied to a section but rather a class, so section_id can be None. 
ITEM3 = {
    "section_id": None,
    "quiz_id": "q3",
    "time_limit": 400,
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

question_to_add= {
    "question_no": 6,
    "isMCQ": True,
    "question_name": "Should you arrive on time to work?",
    "options":["True", "False"],
    "correct_option": 0, #Index 0-> True
    "marks": 1
}

question_to_remove={
    "question_no": 3,
    "isMCQ": False,
    "question_name": "Are you motivated?",
    "options":["True", "False"],
    "correct_option": 0, #True
    "marks": 1
}


class TestQuestion(unittest.TestCase):
    def setUp(self):
        from modules.quiz_manager import Question
        self.test_question = Question(question_to_add)
    
    def tearDown(self):
        self.test_question = None
    
    def test_json(self):
        self.assertTrue(isinstance(self.test_question.json(), dict), "Question JSON is not a dictionary")
        self.assertEqual(question_to_add, self.test_question.json(), "Question JSON does not match")
        self.assertNotEqual(question_to_remove, self.test_question.json(), "Question JSON matched when it should not")


class testQuiz(unittest.TestCase):
    def setUp(self):
        from modules.quiz_manager import Quiz
        self.test_quiz = Quiz(ITEM1)
        self.test_quiz2 = Quiz(ITEM2)

    def tearDown(self):
        del self.test_quiz 
        del self.test_quiz2 

    def test_json(self):
        self.assertTrue(isinstance(self.test_quiz.json(),dict), "Quiz JSON is not a dictionary object")
        self.assertEqual(ITEM1, self.test_quiz.json(), "Quiz does not match")
        self.assertNotEqual(ITEM2, self.test_quiz.json(), "Quiz matched when it should not")
    
    def test_add_question(self):
        from modules.quiz_manager import Question
        self.test_quiz.add_question(Question(question_to_add))
        questions=self.test_quiz.get_questions()

        ITEM1['questions'].append(question_to_add)
        check_against=ITEM1['questions']

        self.assertTrue(question_to_add in [question.json() for question in questions], "Question was not successfully added.")
        self.assertEqual(check_against, [question.json() for question in questions], "Questions do not match, before and after addition")

    def test_remove_question(self):
        check_against=[ITEM2['questions'][1]]

        self.test_quiz2.remove_question(0)
        questions=self.test_quiz2.get_questions()

        self.assertFalse(question_to_remove in [question.json() for question in questions], "Question was not successfully removed.")
        self.assertEqual(check_against, [question.json() for question in questions], "Questions do not match, before and after removal.")


@mock_dynamodb2
class TestQuizDAO(unittest.TestCase):

    def setUp(self):
        from modules import create_tables
        from modules.quiz_manager import QuizDAO 
        self.dynamodb = boto3.resource('dynamodb', region_name= 'ap-southeast-1')
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
        insertTest = self.dao.insert_quiz(ITEM3['section_id'], ITEM3['time_limit'], ITEM3['quiz_id'], ITEM3['questions']).json()
        duplicateTest = self.dao.insert_quiz(ITEM3['section_id'], ITEM3['time_limit'], ITEM3['quiz_id'], ITEM3['questions'])

        self.assertEqual(ITEM3, insertTest, "QuizDAO insert test failure")

        self.assertEqual("Quiz already exists", duplicateTest, "QuizDAO insert duplicate test failure")

    def test_insert_Quiz_w_dict(self):
        insertTest = self.dao.insert_quiz_w_dict(ITEM3)

        self.assertEqual(ITEM3, insertTest.json(), "QuizDAO insert test with dictionary failure")
        with self.assertRaises(ValueError, msg = "Failed to prevent duplicate insert") as context:
            self.dao.insert_quiz_w_dict(ITEM2)

        self.assertTrue("Quiz already exists" == str(context.exception))


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
        from modules.quiz_manager import Quiz, Question
        quizObj = Quiz(ITEM1)
        quizObj.add_question(Question(question_to_add))
        self.dao.update_quiz(quizObj)
        toCheck = Quiz(self.table.get_item(Key={'quiz_id':quizObj.get_quiz_id(), 'section_id':quizObj.get_section_id()})['Item'])

        self.assertEqual(quizObj.json(), toCheck.json(), "QuizDAO update test failure")


    def test_delete_quiz(self):
        from modules.quiz_manager import Quiz
        quizObj = Quiz(ITEM2)
        self.dao.delete_quiz(quizObj)
        key = {'quiz_id':quizObj.get_quiz_id(), 'section_id': quizObj.get_section_id()}
        with self.assertRaises(Exception, msg="QuizDAO did not delete quiz, test failure"):
            self.table.get_item(Key = key)['Item']


if __name__ == "__main__":
    unittest.main()