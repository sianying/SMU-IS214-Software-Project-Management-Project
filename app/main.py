from flask import Flask, request, json, jsonify
from flask_cors import CORS
import boto3
import os
from decimal import Decimal
from modules.course_manager import CourseDAO
from modules.class_manager import ClassDAO


os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./aws_credentials"

class JSONEncoder_Improved(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder= JSONEncoder_Improved
CORS(app)

# ============= Read ===================

@app.route("/courses")
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
    ), 404

@app.route("/classes/<string:course_id>")
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
    ), 404


# ============= Create ==================
@app.route("/courses", methods =['POST'])
def create_course():
    data = request.get_json()
    dao = CourseDAO()
    try:
        results = dao.insert_course_w_dict(data)
        return jsonify(
            {
                "code": 201,
                "data": results.json()
            }
        ), 201
    except ValueError as e:
        if str(e) == "Course already exists":
            return jsonify(
                {
                    "code": 409,
                    "data": str(e)
                }
            ), 409
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the course."
            }
        ), 500
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the course."
            }
        ), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug= True)