from flask import Flask, request, json, jsonify
from flask_cors import CORS
import boto3
import os
import re
from botocore.errorfactory import ClientError
from decimal import Decimal
from modules.attempt_manager import AttemptDAO
from modules.course_manager import CourseDAO
from modules.class_manager import ClassDAO, Class
from modules.staff_manager import StaffDAO
from modules.section_manager import SectionDAO, Material
from modules.quiz_manager import QuizDAO
from modules.trainer_manager import TrainerDAO
from modules.request_manager import RequestDAO

try:
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./aws_credentials"
    session = boto3.Session()
except:
    session = boto3.Session(profile_name="EC2")


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

# retrieve those that can teach a course, not those that are currently teaching the course.
# for HR
@app.route("/courses/qualified/<string:course_id>")
def retrieve_qualified_trainers(course_id):
    dao = TrainerDAO()
    trainer_list = dao.retrieve_qualified_trainers(course_id)
    if len(trainer_list):
        return jsonify(
            {
                "code":200,
                'data': [trainerObj.json() for trainerObj in trainer_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No trainer found"
        }
    ), 404

# retrieve all the courses that a trainer is actually teaching.
# class_list is filtered to only include classes that the trainer is teaching.
# for Trainer
@app.route("/courses/assigned/<string:staff_id>")
def retrieve_courses_trainer_teaches(staff_id):
    dao=TrainerDAO()
    try:
        course_ids = dao.retrieve_courses_teaching(staff_id)
    except:
        return jsonify(
        {
            "code": 404,
            "data": "No trainer found for the given staff_id."
        }
    ), 404
    
    if course_ids==[]:
        return jsonify(
        {
            "code": 404,
            "data": "No courses were found for the trainer."
        }
    ), 404
    
    course_dao = CourseDAO()
    course_list=[]
    for course_id in course_ids:
        try:
            courseObj=course_dao.retrieve_one(course_id)
        except:
            return jsonify(
                {
                    "code": 404,
                    'data': "Course with course_id " + course_id + " could not be found."
                }
            )
        course_list.append(courseObj)

    return jsonify(
        {
            "code":200,
            'data': [courseObj.json() for courseObj in course_list]
        }
    )
    
@app.route("/class/assigned/<string:course_id>/<string:staff_id>")
def retrieve_assigned_classes(course_id, staff_id):
    dao = ClassDAO()
    class_list = dao.retrieve_trainer_classes(course_id, staff_id)

    try:
        class_list = dao.retrieve_trainer_classes(course_id, staff_id)
        
        return jsonify(
            {
                "code":200,
                'data': [classObj.json() for classObj in class_list]
            }
        )
    
    except ValueError as e:
        if str(e) == "No classes found for the given course_id " + course_id:
            return jsonify(
                {
                    "code": 403,
                    "data": str(e)
                }
            ), 403
        
    except:
        return jsonify(
            {
            "code": 404,
            "data": "An error occured while retrieving classes a trainer is assigned to teach."
            }
        )


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

@app.route("/request")
def retrieve_all_pending():
    dao = RequestDAO()
    request_list = dao.retrieve_all_pending()

    if len(request_list):
        return jsonify(
            {
                "code": 200,
                "data": [requestObj.json() for requestObj in request_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No pending requests found"
        }
    ), 404

@app.route("/request/<string:staff_id>")
def retrieve_all_request_by_staff(staff_id):
    dao = RequestDAO()
    request_list = dao.retrieve_all_from_staff(staff_id)

    if len(request_list):
        return jsonify(
            {
                "code": 200,
                "data": [requestObj.json() for requestObj in request_list]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "data": "No requests found"
        }
    ), 404



# ============= Create ==================
@app.route("/courses", methods =['POST'])
def insert_course():
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
        correct_answers.append(question.get_correct_option())
        marks.append(question.get_marks())

    data = request.get_json()
    dao = AttemptDAO()

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
                "data": "An error occurred when creating the attempt." + str(e)
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

@app.route("/section", methods=['POST'])
def insert_section():
    data = request.get_json()

    if "course_id" not in data or "class_id" not in data:
        return jsonify(
            {
                "code":400,
                "data": "course_id or class_id not in Request Body"
            }
        ), 400
    
    class_dao = ClassDAO()
    class_obj = class_dao.retrieve_one(data['course_id'], data['class_id'])
    if class_obj == None:
        return jsonify(
            {
                "code":400,
                "data": "Class does not exist"
            }
        ), 400
    
    section_dao = SectionDAO()
    try:
        results = section_dao.insert_section_w_dict(data)
        class_obj.add_section(results.get_section_id())
        class_dao.update_class(class_obj)
        return jsonify(
            {
                "code": 201,
                "data": results.json()
            }
        ), 201
    except ValueError as e:
        if str(e) == "Section already exists":
            return jsonify(
                {
                    "code": 403,
                    "data": str(e)
                }
            ), 403
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the section."
            }
        ), 500
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when creating the section."
            }
        ), 500

@app.route("/materials/file",methods =['POST'])
def insert_files():
    try:
        file = request.files.get('file')
        section_id = request.form.get('section_id')
    except Exception as e:
        return jsonify({
            "code": 400,
            "data": "Error in uploading file " + str(e)
        })
    
    section_dao = SectionDAO()
    section = section_dao.retrieve_one(section_id)
    
    if section == None:
        return jsonify({
            "code": 404,
            "data": "Section {} does not exist".format(section_id)
        }), 404

    filename, extension = os.path.splitext(file.filename)
    transformed_name = transform_file_name(filename, extension)
    try:
        url = upload_file(file, transformed_name)
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": str(e)
            }
        ), 500

    mat = Material(transformed_name, extension, url)
    section.add_material(mat)
    
    try:
        section_dao.update_section(section)
        return jsonify(
            {
                "code": 201,
                "data": mat.json()
            }
        ),201
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when updating section object."
            }
        ), 500

@app.route("/materials/link", methods = ['POST'])
def insert_links():
    data = request.get_json()

    if "section_id" not in data:
        return jsonify(
            {
                "code": 400,
                "data": "section_id not in Request Body"
            }
        ), 400
    
    section_dao = SectionDAO()
    section = section_dao.retrieve_one(data['section_id'])
    
    if section == None:
        return jsonify({
            "code": 404,
            "data": "Section {} does not exist".format(data['section_id'])
        }), 404

    try:
        mat = Material(data['mat_name'], data['mat_type'], data['url'])
    except:
        return jsonify(
            {
                "code": 400,
                "data": "In proper request body."
            }
        ), 400
    
    section.add_material(mat)
    
    try:
        section_dao.update_section(section)
        return jsonify(
            {
                "code": 201,
                "data": mat.json()
            }
        ), 201
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when updating section object."
            }
        ), 500

@app.route("/request", methods =['POST'])
def insert_request():
    data = request.get_json()
    if "staff_id" not in data or "course_id" not in data or "class_id" not in data:
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
        request_dao = RequestDAO()
        requestObj = request_dao.insert_request_w_dict(data)

        return jsonify(
            {
                "code": 201,
                "data": requestObj.json()
            }
        ), 201
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when inserting request" + str(e)
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

@app.route("/class/edit", methods = ['PUT'])
def edit_class():
    data = request.get_json()
    if "course_id" not in data or "class_id" not in data:
        return jsonify(
            {
                "code": 400,
                "data": "course_id or class_id not in Request Body"
            }
        )
    
    class_dao = ClassDAO()

    class_obj = class_dao.retrieve_one(data['course_id'], data['class_id'])

    if class_obj == None:
        return jsonify(
            {
                "code": 404,
                "data": "Class does not exist."
            }
        )

    if "class_size" in data:
        class_obj.set_class_size(data['class_size'])
    
    if "start_datetime" in data:
        class_obj.set_start_datetime(data['start_datetime'])

    if 'end_datetime' in data:
        class_obj.set_end_datetime(data['end_datetime'])
    
    try:
        class_dao.update_class(class_obj)
        return jsonify(
            {
                "code": 200,
                "data": "Class Updated"
            }
        )
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": "An error occurred when assigning staff"
            }
        ), 500

# ============= Utility ==================

def check_exist(key):
    try:
        session.client('s3', region_name = "ap-southeast-1").head_object(Bucket="spmprojectbucket",Key=key)
        return True
    except ClientError as e:
        return False

def transform_file_name(orig_filename, extension):
    transformed_name = re.sub("[^A-Za-z0-9-_]+",'-', orig_filename)
    version = 1

    while check_exist(transformed_name+"_"+str(version)+extension):
        version += 1

    transformed_name += "_"+str(version)+extension

    return transformed_name

def upload_file(file_binary, filename):
    """
    Function to upload a file to an S3 bucket
    """

    s3_client = session.client('s3', region_name = "ap-southeast-1")
    try:
        s3_client.upload_fileobj(file_binary, "spmprojectbucket", filename, ExtraArgs={'ACL': 'public-read'})
        
        if check_exist(filename):
            return "https://s3.ap-southeast-1.amazonaws.com/spmprojectbucket/"+filename
        
        raise Exception("Error occured when uploading.")
    except Exception as e:
        raise Exception("Error occured when uploading.\nError Message: "+str(e))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug= True)