from flask import request
from . import routes
from .utility import *
from modules.class_manager import ClassDAO
from modules.course_manager import CourseDAO
from modules.staff_manager import StaffDAO
from modules.trainer_manager import TrainerDAO
from modules.request_manager import RequestDAO

# ============= Read ===================
@routes.route("/class/assigned/<string:course_id>/<string:staff_id>")
def retrieve_assigned_classes(course_id, staff_id):
    class_dao = ClassDAO()

    try:
        class_list = class_dao.retrieve_trainer_classes(course_id, staff_id)
        return format_response(200, [classObj.json() for classObj in class_list])
    except ValueError as e:
        return format_response(403, str(e))
    except:
        return format_response(500, "An error occurred while retrieving classes a trainer is assigned to teach.")

@routes.route("/class/<string:course_id>")
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

@routes.route('/classes/enrolled/<string:staff_id>/<string:course_id>')
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

# ============= Create ==================
@routes.route("/class", methods =['POST'])
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

# ============= Update ==================
@routes.route("/class/enroll", methods=['PUT'])
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

        request_dao = RequestDAO()
        request_obj = request_dao.retrieve_one(data['staff_id'], data['course_id'])

        if request_obj != None:
            request_obj.update_req_status("approved")
            request_dao.update_request(request_obj)

        return format_response(200, "Staff enrolled")
    except ValueError as e:
        return format_response(403, str(e))
    except Exception as e:
        return format_response(500, "An error occurred when enrolling staff")


@routes.route("/class/trainer", methods = ['PUT'])
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


@routes.route("/class/edit", methods = ['PUT'])
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

