from flask import Flask, request, json, jsonify
from flask_cors import CORS
import boto3
import os
from decimal import Decimal
from modules.course_manager import CourseDAO
from modules.class_manager import ClassDAO
from modules.staff_manager import StaffDAO
from modules.section_manager import SectionDAO
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

@app.route("/courses/eligible/<string:staff_id>")
def retrieve_eligible_courses(staff_id):
    dao = StaffDAO()
    course_list = dao.retrieve_all_eligible_to_enroll(staff_id)
    if len(course_list):
        return jsonify(
            {
                "code":200,
                'data': [course.json() for course in course_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No courses found"
        }
    ), 404

@app.route("courses/qualified/<string:course_id>")
def retrieve_trainers_can_teach_course(course_id):
    dao = StaffDAO()
    staff_list = dao.retrieve_all_trainers_can_teach(course_id)
    if len(staff_list):
        return jsonify(
            {
                "code":200,
                'data': [staffObj.json() for staffObj in staff_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No staff found"
        }
    ), 404

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
    ), 404

@app.route("/section/<string:course_id>/<int:class_id>")
def retrieve_all_section_from_class(course_id, class_id):
    dao = SectionDAO()
    section_list = dao.retrieve_all_from_class(course_id, class_id)
    if len(section_list):
        return jsonify(
            {
                "code": 200,
                "data": [sectionObj.json() for sectionObj in section_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No section found for Course {}, Class {}".format(course_id, class_id)
        }
    ), 404

@app.route("/section/<string:section_id>")
def retrieve_specific_section(section_id):
    dao = SectionDAO()
    section = dao.retrieve_one(section_id)

    if section != None:
        return jsonify(
            {
                "code":200,
                "data": section.json()
            }
        )

    return jsonify(
        {
            "code": 404,
            "data": "No section found with id "+section_id
        }
    ), 404

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
                    "code": 403,
                    "data": str(e)
                }
            ), 403
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

@app.route("/quiz/create", methods=['POST'])
def insert_quiz():
    data=request.get_json()

    dao = QuizDAO()
    try:
        results = dao.insert_quiz_w_dict(data)
        section_dao = SectionDAO()
        sectionObj = section_dao.retrieve_one(results.get_section_id())
        sectionObj.add_quiz(results.get_quiz_id())
        section_dao.update_section(sectionObj)

        return jsonify(
            {
                "code": 201,
                "data": results.json()
            }
        ), 201
    except ValueError as e:
        if str(e) == "Quiz already exists":
            return jsonify(
                {
                    "code": 403,
                    "data": str(e)
                }
            ), 403
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the quiz."
            }
        ), 500
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the quiz."
            }
        ), 500

# ============= Update ==================
@app.route("/class/enroll", methods=['PUT'])
def enroll_learners():
    data = request.get_json()

    if "course_id" not in data or "class_id" not in data or "staff_id" not in data:
        return jsonify(
            {
                "code": 400,
                "data": "course_id, class_id or staff_id not in Request Body"
            }
        ), 400

    class_dao = ClassDAO()
    class_to_enroll = class_dao.retrieve_one(data['course_id'], data['class_id'])
    staff_dao = StaffDAO()
    staff = staff_dao.retrieve_one(data['staff_id'])

    if class_to_enroll == None or staff == None:
        return jsonify(
            {
                "code": 404,
                "data": "Class or Staff to enroll not found"
            }
        ), 404


    try:
        class_to_enroll.enrol_learner(data['staff_id'])
    except ValueError as e:
        return jsonify(
            {
                "code":403,
                "data": str(e)
            }
        ), 403
    
    try:
        staff.add_enrolled(data['course_id'])
    except ValueError as e:
        return jsonify(
            {
                "code": 403,
                "data": str(e)
            }
        ), 403

    try:
        staff_dao.update_staff(staff)
        class_dao.update_class(class_to_enroll)

        return jsonify(
            {
                "code": 200,
                "data": "Staff enrolled"
            }
        )
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when enrolling staff"
            }
        ), 500






if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug= True)