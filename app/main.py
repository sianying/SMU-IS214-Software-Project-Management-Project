from flask import Flask, request, json, jsonify
from flask_cors import CORS
import boto3
import os
import re
from botocore.errorfactory import ClientError
from decimal import Decimal
from modules.attempt_manager import AttemptDAO
from modules.course_manager import CourseDAO
from modules.class_manager import ClassDAO
from modules.staff_manager import StaffDAO
from modules.section_manager import SectionDAO, Material
from modules.quiz_manager import QuizDAO
from modules.trainer_manager import TrainerDAO
from modules.request_manager import RequestDAO, Request
from modules.progress_manager import ProgressDAO

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
    course_dao = CourseDAO()
    course_list = course_dao.retrieve_all()
    if len(course_list):
        return format_response(200, [course.json() for course in course_list])
    
    return format_response(404, "No courses found")


@app.route("/courses/eligible/<string:staff_id>")
def retrieve_eligible_courses(staff_id):
    staff_dao = StaffDAO()
    staff = staff_dao.retrieve_one(staff_id)

    if staff == None:
        return format_response(404, "Staff "+staff_id+" does not exist.")

    # if staff is Trainer, need to remove courses he is enrolled in + assigned to teach as well.
    courses_to_remove=staff.get_courses_enrolled()

    if staff.get_isTrainer():
        trainer_dao = TrainerDAO()
        trainer = trainer_dao.retrieve_one(staff_id)
        courses_to_remove += trainer.get_courses_can_teach()

    course_dao = CourseDAO()
    course_list = course_dao.retrieve_eligible_course(staff.get_courses_completed(), courses_to_remove)

    if len(course_list):
        return format_response(200, [course.json() for course in course_list])
    return format_response(404, "No courses found.")


@app.route("/course/<string:course_id>")
def retrieve_specific_course(course_id):
    course_dao = CourseDAO()
    course = course_dao.retrieve_one(course_id)

    if course != None:
        return format_response(200, course.json())

    return format_response(404, "No course found with id "+course_id)

# retrieve those that can teach a course, not those that are currently teaching the course.
# for HR
@app.route("/courses/qualified/<string:course_id>")
def retrieve_qualified_trainers(course_id):
    trainer_dao = TrainerDAO()
    trainer_list = trainer_dao.retrieve_qualified_trainers(course_id)
    if len(trainer_list):
        return format_response(200, [trainerObj.json() for trainerObj in trainer_list])
    
    return format_response(404, "No trainer found.")


# retrieve all the courses that a trainer is actually teaching.
# class_list is filtered to only include classes that the trainer is teaching.
# for Trainer
@app.route("/courses/assigned/<string:staff_id>")
def retrieve_courses_trainer_teaches(staff_id):
    trainer_dao=TrainerDAO()
    try:
        course_ids = trainer_dao.retrieve_courses_teaching(staff_id)
    except:
        return format_response(404, "No trainer found for staff_id "+staff_id)
    
    if course_ids==[]:
        return format_response(404, "No courses were found for the trainer.")
    
    course_dao = CourseDAO()
    course_list=[]
    for course_id in course_ids:
        courseObj=course_dao.retrieve_one(course_id)

        if courseObj==None:
            return format_response(404, "Course with course_id "+course_id +" could not be found.")

        course_list.append(courseObj)

    return format_response(200, [courseObj.json() for courseObj in course_list])
    

@app.route("/class/assigned/<string:course_id>/<string:staff_id>")
def retrieve_assigned_classes(course_id, staff_id):
    class_dao = ClassDAO()
    class_list = class_dao.retrieve_trainer_classes(course_id, staff_id)

    try:
        class_list = class_dao.retrieve_trainer_classes(course_id, staff_id)
        return format_response(200, [classObj.json() for classObj in class_list])

    except ValueError as e:
        return format_response(403, str(e))
        
    except:
        return format_response(500, "An error occurred while retrieving classes a trainer is assigned to teach.")


@app.route("/staff/<string:staff_id>")
def retrieve_specific_staff(staff_id):
    staff_dao = StaffDAO()
    staffObj = staff_dao.retrieve_one(staff_id)
    if staffObj != None:
        return format_response(200, staffObj.json())
    return format_response(404,"No staff found with staff_id "+ staff_id)


@app.route("/staff/eligible/<string:course_id>")
def retrieve_eligible_staff(course_id):
    course_dao = CourseDAO()
    courseObj = course_dao.retrieve_one(course_id)

    if courseObj == None:
        return format_response(404, course_id + " does not exist.")
    
    staff_dao = StaffDAO()
    staff_list = staff_dao.retrieve_eligible_staff_to_enrol(courseObj)

    if len(staff_list):
        return format_response(200, [staff.json() for staff in staff_list])
    
    return format_response(404, "No staff found.")


@app.route("/class/<string:course_id>")
def retrieve_all_classes(course_id):
    class_dao = ClassDAO()
    class_list = class_dao.retrieve_all_from_course(course_id)
    staff_dao = StaffDAO()
    toReturn = []

    for classObj in class_list:
        class_json = classObj.json()
        if classObj.get_trainer_assigned() != None:
            class_json['trainer_name'] = staff_dao.retrieve_one(classObj.get_trainer_assigned()).get_staff_name()
        else:
            class_json['trainer_name'] = None

        toReturn.append(class_json)


    if len(class_list):
        return format_response(200, toReturn)
    
    return format_response(404, "No classes found for course " + course_id)


@app.route("/section/<string:course_id>/<int:class_id>")
def retrieve_all_section_from_class(course_id, class_id):
    section_dao = SectionDAO()
    section_list = section_dao.retrieve_all_from_class(course_id, class_id)
    if len(section_list):
        return format_response(200, [sectionObj.json() for sectionObj in section_list])
    
    return format_response(404, "No section found for Course {}, Class {}".format(course_id, class_id))


@app.route("/section/<string:section_id>")
def retrieve_specific_section(section_id):
    section_dao = SectionDAO()
    section = section_dao.retrieve_one(section_id)

    if section != None:
        return format_response(200, section.json())

    return format_response(404, "No section found with id "+section_id)


@app.route("/quiz/<string:quiz_id>")
def retrieve_quiz_by_ID(quiz_id):
    quiz_dao = QuizDAO()
    quizObj = quiz_dao.retrieve_one(quiz_id)

    if quizObj:
        return format_response(200, quizObj.json())
    
    return format_response(404, "No quiz was found with id "+quiz_id)


@app.route("/quiz/section/<string:section_id>")
def retrieve_quiz_by_section(section_id):
    quiz_dao = QuizDAO()
    quizObj = quiz_dao.retrieve_by_section(section_id)

    if quizObj:
        return format_response(200, quizObj.json())
    
    return format_response(404, "No quiz was found for section "+ section_id)


@app.route("/attempts/<string:quiz_id>")
def retrieve_quiz_attempts(quiz_id):
    attempt_dao = AttemptDAO()
    attempts_list = attempt_dao.retrieve_by_quiz(quiz_id)

    if len(attempts_list):
        return format_response(200, [attemptObj.json() for attemptObj in attempts_list])
    
    return format_response(404, "No attempts were found for Quiz {}".format(quiz_id))


@app.route("/attempts/<string:quiz_id>/<string:staff_id>")
def retrieve_quiz_attempts_by_learner(quiz_id, staff_id):
    attempt_dao = AttemptDAO()
    attempts_list = attempt_dao.retrieve_by_learner(quiz_id, staff_id)

    if len(attempts_list):
        return format_response(200, [attemptObj.json() for attemptObj in attempts_list])
    
    return format_response(404, "No attempts were found for Quiz {}".format(quiz_id))


@app.route("/request")
def retrieve_all_pending():
    request_dao = RequestDAO()
    request_list = request_dao.retrieve_all_pending()
    staff_dao = StaffDAO()
    toReturn = []

    for requestObj in request_list:
        staff_name = staff_dao.retrieve_one(requestObj.get_staff_id()).get_staff_name()
        request_json = requestObj.json()
        request_json['staff_name'] = staff_name
        toReturn.append(request_json)


    if len(request_list):
        return format_response(200, toReturn)
    
    return format_response(404, "No pending requests found")

@app.route("/request/<string:staff_id>")
def retrieve_all_request_by_staff(staff_id):
    request_dao = RequestDAO()
    request_list = request_dao.retrieve_all_from_staff(staff_id)

    if len(request_list):
        return format_response(200, [requestObj.json() for requestObj in request_list])
    
    return format_response(404, "No requests found")


@app.route("/progress/<string:staff_id>/<string:course_id>")
def check_learner_progress(staff_id, course_id):
    progress_dao = ProgressDAO()
    progressObj = progress_dao.retrieve_by_learner_and_course(staff_id, course_id)

    if progressObj:
        return format_response(200, progressObj.json())
    
    return format_response(404, "Could not find any progress for staff {} and course {}".format(staff_id, course_id))


# ============= Create ==================
@app.route("/courses", methods =['POST'])
def insert_course():
    data = request.get_json()
    course_dao = CourseDAO()
    try:
        results = course_dao.insert_course_w_dict(data)
        return format_response(201, results.json())
    except ValueError as e:
        if str(e) == "Course already exists":
            return format_response(403, str(e))
        return format_response(500, "An error occurred when creating the course")
    except Exception as e:
        return format_response(500, "An error occurred when creating the course")


@app.route("/quiz/create", methods=['POST'])
def insert_quiz():
    data=request.get_json()
    quiz_dao = QuizDAO()

    is_final_quiz = False
    if 'is_final_quiz' in data:
        is_final_quiz = True
        course_id = data['course_id']
        class_id = data['class_id']
    
    try:
        results = quiz_dao.insert_quiz_w_dict(data)
        
    except ValueError as e:
        if str(e) == "Quiz already exists":
            return format_response(403, str(e))
        return format_response(500, "An error occured when creating the quiz.")
    except Exception as e:
        return format_response(500, "An error occured when creating the quiz.")


    #if quiz is a final graded quiz, need to update class object too.
    if is_final_quiz:
        class_dao = ClassDAO()
        try:
            classObj = class_dao.retrieve_one(course_id, class_id)
            classObj.set_final_quiz_id(results.get_quiz_id())
            class_dao.update_class(classObj)
        except ValueError as e:
            if "Update Failure with code:" in str(e):
                return format_response(403, str(e) + ' for final graded quiz.')
            
            return format_response(500, "An error occurred when updating class for final graded quiz.")
        except Exception as e:
            return format_response(500, "An error occurred when updating class for final graded quiz.")
    
    #UPDATE SECTION OBJECT TOO, if quiz is not FINAL and not GRADED
    else:
        section_dao = SectionDAO()
        try:
            sectionObj = section_dao.retrieve_one(results.get_section_id())
            sectionObj.add_quiz(results.get_quiz_id())
            section_dao.update_section(sectionObj)
        except ValueError as e:
            if "Update Failure with code:" in str(e):
                return format_response(403, str(e) + ' for ungraded quiz.')
            return format_response(500, "An error occurred when updating section for ungraded quiz.")
        except Exception as e:
            return format_response(500, "An error occurred when updating section for ungraded quiz.")
    
    return format_response(201, results.json())


@app.route("/attempts", methods=['POST'])
def insert_attempt():
    data = request.get_json()

    quiz_dao = QuizDAO()
    quiz_obj = quiz_dao.retrieve_one(data['quiz_id'])

    if quiz_obj == None:
        return format_response(404, "No quiz was found with id "+data['quiz_id'])

    quiz_questions = quiz_obj.get_questions()

    correct_answers=[]
    marks=[]
    for question in quiz_questions:
        correct_answers.append(question.get_correct_option())
        marks.append(question.get_marks())

    is_final_quiz = False

    if 'is_final_quiz' in data:
        is_final_quiz = True
        data.pop('is_final_quiz')

    attempt_dao = AttemptDAO()

    try:
        results = attempt_dao.insert_attempt(data, correct_answers, marks) 
        
    except ValueError as e:
        if str(e) == "Attempt already exists":
            return format_response(403, str(e))
        return format_response(500, "An error occurred when creating the attempt.")
    except Exception as e:
        return format_response(500, "An error occurred when creating the attempt.")

    try:
        progress_dao = ProgressDAO()
        progressObj = progress_dao.retrieve_by_learner_and_course(data['staff_id'], data['course_id'])

        if is_final_quiz:
            # results stands for the attempt object created
            current_score = results.get_overall_score()
            total_score = quiz_obj.get_total_marks()

            if current_score >= 0.85* total_score:
                progressObj.set_final_quiz_passed(True)
        else:
            progressObj.add_completed_section(quiz_obj.get_section_id())

        progress_dao.update_progress(progressObj)

        return format_response(201, results.json())
    except Exception as e:
        return format_response(500, "An error occured when updating the progress.")


@app.route("/class", methods =['POST'])
def insert_class():
    data = request.get_json()

    if "course_id" not in data:
        return format_response(400, "course_id not in Request Body")
    
    course_dao = CourseDAO()

    course = course_dao.retrieve_one(data["course_id"])

    if course == None:
        return format_response(400, "course to insert class in does not exist")

    if "class_id" not in data:
        data["class_id"] = len(course.get_class_list())+1

    class_dao = ClassDAO()
    
    try:
        results = class_dao.insert_class_w_dict(data)
        course.add_class(results.get_class_id())
        course_dao.update_course(course)
        return format_response(201, results.json())
    except ValueError as e:
        if str(e) == "Class already exists":
            return format_response(403, str(e))

        return format_response(500, "An error occurred when creating the class.")
    except Exception as e:
        return format_response(500, "An error occurred when creating the class.")

@app.route("/section", methods=['POST'])
def insert_section():
    data = request.get_json()

    if "course_id" not in data or "class_id" not in data:
        return format_response(400, "course_id or class_id not in Request Body")
    
    class_dao = ClassDAO()
    class_obj = class_dao.retrieve_one(data['course_id'], data['class_id'])
    if class_obj == None:
        return format_response(400, "Class does not exist")
    
    section_dao = SectionDAO()
    try:
        results = section_dao.insert_section_w_dict(data)
        class_obj.add_section(results.get_section_id())
        class_dao.update_class(class_obj)
        return format_response(201, results.json())
    except ValueError as e:
        if str(e) == "Section already exists":
            return format_response(403, str(e))
        
        return format_response(500, "An error occurred when creating the section.")
    except Exception as e:
        return format_response(500, "An error occurred when creating the section.")


@app.route("/materials/file",methods =['POST'])
def insert_files():
    try:
        file = request.files.get('file')
        section_id = request.form.get('section_id')
    except Exception as e:
        return format_response(400, "Error in uploading file "+str(e))
    
    section_dao = SectionDAO()
    section = section_dao.retrieve_one(section_id)
    
    if section == None:
        return format_response(404, "Section {} does not exist".format(section_id))

    filename, extension = os.path.splitext(file.filename)
    transformed_name = transform_file_name(filename, extension)
    try:
        url = upload_file(file, transformed_name)
    except Exception as e:
        return format_response(500, str(e))
    
    mat = Material({"mat_name":transformed_name, "mat_type":extension, "url":url})
    section.add_material(mat)
    
    try:
        section_dao.update_section(section)
        return format_response(201, mat.json())
    except Exception as e:
        return format_response(500, "An error occurred when updating section object.")


@app.route("/materials/link", methods = ['POST'])
def insert_links():
    data = request.get_json()

    if "section_id" not in data:
        return format_response(400, "section_id not in Request Body")
    
    section_dao = SectionDAO()
    section = section_dao.retrieve_one(data['section_id'])
    
    if section == None:
        return format_response(404, "Section {} does not exist".format(data['section_id']))

    try:
        mat = Material(data['mat_name'], data['mat_type'], data['url'])
    except:
        return format_response(400, "Not proper request body.")
    
    section.add_material(mat)
    
    try:
        section_dao.update_section(section)
        return format_response(201, mat.json())
    except Exception as e:
        return format_response(500, "An error occurred when updating section object.")


@app.route("/request", methods =['POST'])
def insert_request():
    data = request.get_json()
    if "staff_id" not in data or "course_id" not in data or "class_id" not in data:
        return format_response(400, "course_id, class_id or staff_id not in Request Body")
    
    class_dao = ClassDAO()
    class_to_enroll = class_dao.retrieve_one(data['course_id'], data['class_id'])
    staff_dao = StaffDAO()
    staff = staff_dao.retrieve_one(data['staff_id'])

    if class_to_enroll == None or staff == None:
        return format_response(404, "Class or Staff to enroll not found")
    
    try:
        request_dao = RequestDAO()
        requestObj = request_dao.insert_request_w_dict(data)
        return format_response(201, requestObj.json())
    except Exception as e:
        return format_response(500, "An error occurred when inserting request")


# ============= Update ==================
@app.route("/class/enroll", methods=['PUT'])
def enroll_learners(data = None):
    if data == None:
        data = request.get_json()

    if "course_id" not in data or "class_id" not in data or "staff_id" not in data:
        return format_response(400, "course_id, class_id or staff_id not in Request Body")

    class_dao = ClassDAO()
    class_to_enroll = class_dao.retrieve_one(data['course_id'], data['class_id'])
    staff_dao = StaffDAO()
    staff = staff_dao.retrieve_one(data['staff_id'])

    if class_to_enroll == None or staff == None:
        return format_response(404, "Class or Staff to enroll not found")


    try:
        class_to_enroll.enrol_learner(data['staff_id'])
        staff.add_enrolled(data['course_id'])
        staff_dao.update_staff(staff)
        class_dao.update_class(class_to_enroll)
        return format_response(200, "Staff enrolled")
    except ValueError as e:
        return format_response(403, str(e))
    except Exception as e:
        return format_response(500, "An error occurred when enrolling staff")


@app.route("/class/trainer", methods = ['PUT'])
def assign_trainer():
    data = request.get_json()

    if "course_id" not in data or "class_id" not in data or "staff_id" not in data:
        return format_response(400, "course_id, class_id or staff_id not in Request Body")

    class_dao = ClassDAO()
    class_to_assign = class_dao.retrieve_one(data['course_id'], data['class_id'])
    staff_dao = StaffDAO()
    staff = staff_dao.retrieve_one(data['staff_id'])

    if class_to_assign == None or staff == None:
        return format_response(404, "Class or Staff to assign not found")


    try:
        class_to_assign.set_trainer(data['staff_id'])
        class_dao.update_class(class_to_assign)
    except ValueError as e:
        return format_response(500, "An error occurred when updating class: "+ str(e))
    except Exception as e:
        return format_response(500, "An error occurred when updating class: "+ str(e))


    try:
        trainer_dao = TrainerDAO()
        trainerObj = trainer_dao.retrieve_one(data['staff_id'])
        if data['course_id'] not in trainerObj.get_courses_teaching():
            trainerObj.add_course_teaching(data['course_id'])
            trainer_dao.update_trainer(trainerObj)

        return format_response(200, "Staff assigned")
    except ValueError as e:
        return format_response(500, "An error occurred when updating trainer: "+str(e))
    except Exception as e:
        return format_response(500, "An error occurred when updating trainer: "+str(e))


@app.route("/class/edit", methods = ['PUT'])
def edit_class():
    data = request.get_json()
    if "course_id" not in data or "class_id" not in data:
        return format_response(400, "course_id or class_id not in Request Body")
    
    class_dao = ClassDAO()

    class_obj = class_dao.retrieve_one(data['course_id'], data['class_id'])

    if class_obj == None:
        return format_response(404, "Class does not exist.")

    if "class_size" in data:
        class_obj.set_class_size(data['class_size'])
    
    if "start_datetime" in data:
        class_obj.set_start_datetime(data['start_datetime'])

    if 'end_datetime' in data:
        class_obj.set_end_datetime(data['end_datetime'])
    
    try:
        class_dao.update_class(class_obj)
        return format_response(200, "Class Updated")
    except Exception as e:
        return format_response(500, "An error occurred when assigning staff")


@app.route("/quiz/update", methods=['PUT'])
def update_quiz():
    data = request.get_json()
    if "quiz_id" not in data:
        return format_response(400, "quiz_id not in Request Body")

    quiz_dao = QuizDAO()
    quizObj = quiz_dao.retrieve_one(data['quiz_id'])

    if quizObj==None:
        return format_response(404, "Quiz does not exist.")

    # Before updating, check if any attempts have been made before
    attempt_dao = AttemptDAO()
    attempt_list = attempt_dao.retrieve_by_quiz(data['quiz_id'])

    if len(attempt_list):
        return format_response(401, "Quiz cannot be updated because there are already existing attempts.")

    if "time_limit" in data:
        quizObj.set_time_limit(data['time_limit'])

    if "questions" in data:
        quizObj.set_questions(data['questions'])
    
    try:
        quiz_dao.update_quiz(quizObj)
        return format_response("Quiz Updated")

    except Exception as e:
        return format_response(500, "An error occurred when updating quiz")


@app.route("/request/update", methods = ['PUT'])
def update_request():
    data = request.get_json()
    if "course_id" not in data or "class_id" not in data or "staff_id" not in data:
        return format_response(400, "course_id, class_id or staff_id not in Request Body")

    request_dao = RequestDAO()
    requestObj = Request(data)
    try:
        request_dao.update_request(requestObj)
        if data['req_status'] == "approved":
            return enroll_learners(data)
        
        return format_response(200, "Staff request rejected")
    except Exception as e:
        return format_response(500, "An error occurred when updating request")

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

def format_response(code, data):
    return jsonify(
        {
            "code": code,
            "data": data
        }
    ), code

# 2 NEW ENDPOINTS- put under GET requests
@app.route('/courses/enrolled/<string:staff_id>')
def retrieve_enrolled_courses(staff_id):
    staff_dao = StaffDAO()
    staff_obj = staff_dao.retrieve_one(staff_id)

    if staff_obj == None:
        return format_response(404, "Staff with staff_id "+ staff_id+" not found.")

    enrolled_course_ids = staff_obj.get_courses_enrolled()
    course_dao = CourseDAO()
    returned_courses = []

    for course_id in enrolled_course_ids:
        course_obj = course_dao.retrieve_one(course_id)

        if course_obj == None:
            return format_response(404, "Course with course_id "+str(course_id)+ " not found.")

        returned_courses.append(course_obj)

    return format_response(200, [course_obj.json() for course_obj in returned_courses])


@app.route('/classes/enrolled/<string:staff_id>/<string:course_id>')
def retrieve_enrolled_classes(staff_id, course_id):
    staff_dao = StaffDAO()
    staff_obj = staff_dao.retrieve_one(staff_id)
    
    if staff_obj==None:
        return format_response(404, "Staff with staff_id "+staff_id +" not found.")

    class_dao = ClassDAO()
    class_list = class_dao.retrieve_all_from_course(course_id)

    if len(class_list)==0:
        return format_response(404, "No classes found for course_id "+ course_id)

    for classObj in class_list:
        learners_enrolled = classObj.get_learners_enrolled()
        if staff_id in learners_enrolled:
            class_json = classObj.json()
            if classObj.get_trainer_assigned() != None:
                class_json['trainer_name'] = staff_dao.retrieve_one(classObj.get_trainer_assigned()).get_staff_name()
            else:
                class_json['trainer_name'] = None
            
            return format_response(200, class_json)

    return format_response(404, "No enrolled classes found for staff "+ staff_id + " and course "+course_id)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug= True)