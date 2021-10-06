from flask import Flask, request, json, jsonify
from flask_cors import CORS
import boto3
import os
from decimal import Decimal
from modules.course_manager import CourseDAO
from modules.class_manager import ClassDAO
from modules.quiz_manager import QuizDAO


os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./aws_credentials"
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

class JSONEncoder_Improved(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder= JSONEncoder_Improved
CORS(app)

@app.route("/course")
def retrieve_all_courses():
    dao = CourseDAO()
    course_list = dao.retrieve_all()
    if len(course_list):
        return jsonify(
            {    
                "code":200,
                "data": [course.json() for course in course_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No courses found"
        }
    )

@app.route("/class/<string:course_id>")
def retrieve_all_classes(course_id):
    dao = ClassDAO()
    class_list = dao.retrieve_all_from_course(course_id)
    if len(class_list):
        return jsonify(
            {    
                "code":200,
                "data": [classObj.json() for classObj in class_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No classes found for course "+course_id
        }
    )

@app.route("/quiz/section=<string:section_id>/questions=<string:questions>", methods=['POST'])
def insert_quiz(section_id, questions, answers):



@app.route("/quiz/<string:quiz_id>")
def retrieve_quiz_by_ID(quiz_id):
    dao = QuizDAO()
    quizObj = dao.retrieve_one(quiz_id)

    if quizObj:
        return jsonify(
            {
                "code":200,
                "data": quizObj.json()
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No quiz was found with id " + quiz_id
        }
    )

@app.route("/quiz/section/<string:section_id>")
def retrieve_quiz_by_section(section_id):
    dao = QuizDAO()
    quizObj = dao.retrieve_one(section_id)

    if quizObj:
        return jsonify(
            {
                "code":200,
                "data": quizObj.json()
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No quiz was found for section " + section_id
        }
    )



if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug= True)