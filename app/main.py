from flask import Flask, request, json, jsonify
from flask_cors import CORS
import boto3
import os
from decimal import Decimal
from modules.attempt_manager import AttemptDAO
from modules.course_manager import CourseDAO
from modules.class_manager import ClassDAO
from modules.staff_manager import StaffDAO
from modules.section_manager import SectionDAO
from modules.quiz_manager import QuizDAO


os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./aws_credentials"
os.environ['AWS_DEFAULT_REGION'] = 'ap-southeast-1'

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
    staff_dao = StaffDAO()
    staff = staff_dao.retrieve_one(staff_id)

    if staff == None:
        return jsonify(
            {
                "code": 404,
                "data": "Staff "+staff_id+" does not exist."
            }
        ), 404

    course_dao = CourseDAO()
    course_list = course_dao.retrieve_eligible_course(staff.get_courses_completed(),staff.get_courses_enrolled())

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

@app.route("/course/<string:course_id>")
def retrieve_specific_course(course_id):
    dao = CourseDAO()
    course = dao.retrieve_one(course_id)

    if course != None:
        return jsonify(
            {
                "code":200,
                "data": course.json()
            }
        )

    return jsonify(
        {
            "code": 404,
            "data": "No course found with id "+course_id
        }
    ), 404


@app.route("/courses/qualified/<string:course_id>")
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

@app.route("/staff/eligible/<string:course_id>")
def retrieve_eligible_staff(course_id):
    course_dao = CourseDAO()
    courseObj = course_dao.retrieve_one(course_id)

    if courseObj == None:
        return jsonify(
            {
                "code":404,
                "data": course_id + " does not exist."
            }
        ), 404
    
    staff_dao = StaffDAO()
    staff_list = staff_dao.retrieve_eligible_staff_to_enrol(courseObj)

    if len(staff_list):
        return jsonify(
            {
                "code":200,
                'data': [staff.json() for staff in staff_list]
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
    quizObj = dao.retrieve_by_section(section_id)

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

@app.route("/attempts/<string:quiz_id>")
def retrieve_quiz_attempts(quiz_id):
    dao = AttemptDAO()
    attempts_list = dao.retrieve_by_quiz(quiz_id)

    if len(attempts_list):
        return jsonify(
            {
                "code": 200,
                "data": [attemptObj.json() for attemptObj in attempts_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No attempts were found for Quiz {}".format(quiz_id)
        }
    ), 404

@app.route("/attempts/<string:quiz_id>/<string:staff_id>")
def retrieve_quiz_attempts_by_learner(quiz_id, staff_id):
    dao = AttemptDAO()
    attempts_list = dao.retrieve_by_learner(quiz_id, staff_id)

    if len(attempts_list):
        return jsonify(
            {
                "code": 200,
                "data": [attemptObj.json() for attemptObj in attempts_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No attempts were found for Quiz {}".format(quiz_id)
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
        

    #UPDATE SECTION OBJECT TOO
    section_dao = SectionDAO()
    try:
        sectionObj = section_dao.retrieve_one(results.get_section_id())
        sectionObj.add_quiz(results.get_quiz_id())
        section_dao.update_section(sectionObj)

        #return the results from successfully inserting the quiz previously
        return jsonify(
            {
                "code": 201,
                "data": results.json()
            }
        ), 201

    #Technically need to delete the quiz from DB
    except ValueError as e:
        if "Update Failure with code:" in str(e):
            return jsonify(
                {
                    "code": 403,
                    "data": str(e)
                }
            ), 403
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when updating the section."
            }
        ), 500
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when updating the section."
            }
        ), 500


@app.route("/attempts/<string:quiz_id>", methods=['POST'])
def insert_attempt(quiz_id):
    quiz_dao = QuizDAO()
    quiz_obj = quiz_dao.retrieve_one(quiz_id)

    if quiz_obj == None:
        return jsonify(
            {
                "code": 404,
                "data": "No quiz was found with id " + quiz_id
            }
        )

    quiz_questions = quiz_obj.get_questions()

    correct_answers=[]
    marks=[]
    for question in quiz_questions:
        # need to create question class and get these attributes as methods?
        correct_answers.append(question['correct_option'])
        marks.append(question['marks'])

    data = request.get_json()
    dao = CourseDAO()

    try:
        results = dao.insert_attempt(data, correct_answers, marks)
        return jsonify(
            {
                "code": 201,
                "data": results.json()
            }
        ), 201
    except ValueError as e:
        if str(e) == "Attempt already exists":
            return jsonify(
                {
                    "code": 403,
                    "data": str(e)
                }
            ), 403
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the attempt."
            }
        ), 500
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the attempt."
            }
        ), 500


@app.route("/class", methods =['POST'])
def insert_class():
    data = request.get_json()

    if "course_id" not in data:
        return jsonify(
            {
                "code": 400,
                "data": "course_id not in Request Body"
            }
        ), 400
    
    course_dao = CourseDAO()

    course = course_dao.retrieve_one(data["course_id"])

    if course == None:
        return jsonify(
            {
                "code": 400,
                "data": "Course to insert class in does not exist"
            }
        ), 400

    if "class_id" not in data:
        data["class_id"] = len(course.get_class_list())+1

    class_dao = ClassDAO()
    
    try:
        results = class_dao.insert_class_w_dict(data)
        course.add_class(results.get_class_id())
        course_dao.update_course(course)
        return jsonify(
            {
                "code": 201,
                "data": results.json()
            }
        ), 201
    except ValueError as e:
        if str(e) == "Class already exists":
            return jsonify(
                {
                    "code": 403,
                    "data": str(e)
                }
            ), 403
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the class." 
            }
        ), 500
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the class."
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

@app.route("/class/trainer", methods = ['PUT'])
def assign_trainer():
    data = request.get_json()

    if "course_id" not in data or "class_id" not in data or "staff_id" not in data:
        return jsonify(
            {
                "code": 400,
                "data": "course_id, class_id or staff_id not in Request Body"
            }
        ), 400

    class_dao = ClassDAO()
    class_to_assign = class_dao.retrieve_one(data['course_id'], data['class_id'])
    staff_dao = StaffDAO()
    staff = staff_dao.retrieve_one(data['staff_id'])

    if class_to_assign == None or staff == None:
        return jsonify(
            {
                "code": 404,
                "data": "Class or Staff to assign not found"
            }
        ), 404

    class_to_assign.set_trainer(data['staff_id'])
    try:
        class_dao.update_class(class_to_assign)

        return jsonify(
            {
                "code": 200,
                "data": "Staff assigned"
            }
        )
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when assigning staff"
            }
        ), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug= True)