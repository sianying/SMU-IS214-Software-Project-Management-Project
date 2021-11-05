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
    ],
    "total_marks":3

}

ITEM2 = {
    "section_id": "s2",
    "quiz_id": "q2",
    "time_limit": 200,
    "questions": [
        {
            "question_no": 1,
            "isMCQ": False,
            "question_name": "Are you motivated?",
            "options":["True", "False"],
            "correct_option": 0, #True
            "marks": 2
        },

        {
            "question_no": 2,
            "isMCQ": True,
            "question_name": "How many days do you work per week",
            "options":["4 days", "5 days", "6 days", "7 days"],
            "correct_option": 1, #5 days
            "marks": 2
        }
    ],
    "total_marks":4
}

# Final Quiz is not tied to a section but rather a class, so section_id can be None. 
ITEM3 = {
    "section_id": None,
    "quiz_id": "q3",
    "time_limit": 400,
    "questions": [
        {
            "question_no": 1,
            "isMCQ": False,
            "question_name": "You enjoyed studying the material provided.",
            "options":["True", "False"],
            "correct_option": 0, #True
            "marks": 5
        },
    ],
    "total_marks": 5
}

question1= {
    "question_no": 1,
    "isMCQ": True,
    "question_name": "Should you arrive on time to work?",
    "options":["True", "False"],
    "correct_option": 0, #Index 0-> True
    "marks": 1
}

question2={
    "question_no": 1,
    "isMCQ": False,
    "question_name": "Are you motivated?",
    "options":["True", "False"],
    "correct_option": 0, #True
    "marks": 1
}


class TestQuestion(unittest.TestCase):
    def setUp(self):
        from modules.quiz_manager import Question
        self.test_question = Question(question1)
    
    def tearDown(self):
        self.test_question = None
    
    def test_json(self):
        self.assertTrue(isinstance(self.test_question.json(), dict), "Question JSON is not a dictionary")
        self.assertEqual(question1, self.test_question.json(), "Question JSON does not match")
        self.assertNotEqual(question2, self.test_question.json(), "Question JSON matched when it should not")


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

    def test_set_question(self):
        initial_questions = self.test_quiz.get_questions()
        initial_marks = self.test_quiz.get_total_marks()

        question_list = [question1, question2]
        self.test_quiz.set_questions(question_list)
        new_questions=self.test_quiz.get_questions()
        new_marks= self.test_quiz.get_total_marks()

        self.assertNotEqual(initial_questions, new_questions, "Questions were not successfully updated")
        self.assertEqual(question_list, [question.json() for question in new_questions], "Questions do not match when they should.")
        self.assertNotEqual(initial_marks, new_marks, "Marks match when they should not. Initially should be 3, After should be 2.")


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

    def test_insert_quiz_w_dict(self):
        insertTest = self.dao.insert_quiz_w_dict(ITEM3)

        self.assertEqual(ITEM3, insertTest.json(), "QuizDAO insert test with dictionary failure")
        with self.assertRaises(ValueError, msg = "Failed to prevent duplicate insert") as context:
            self.dao.insert_quiz_w_dict(ITEM2)

        self.assertTrue("Quiz already exists" == str(context.exception))

    def test_retrieve_one(self):
        self.assertEqual(ITEM1, self.dao.retrieve_one(ITEM1['quiz_id']).json(), "QuizDAO did not retrieve the correct quiz by quiz_id, test failure")
        self.assertEqual(None, self.dao.retrieve_one("fakequizid"), "QuizDAO should have returned nothing, test failure (quiz_id)")

    def test_update_quiz(self):
        from modules.quiz_manager import Quiz, Question
        quizObj = Quiz(ITEM1)
        quizObj.set_questions([question1, question2])
        quizObj.set_time_limit(100)
        self.dao.update_quiz(quizObj)
        toCheck = Quiz(self.table.get_item(Key={'quiz_id':quizObj.get_quiz_id(), 'section_id':quizObj.get_section_id()})['Item'])

        self.assertEqual(quizObj.json(), toCheck.json(), "QuizDAO update test failure")


if __name__ == "__main__":
    unittest.main()