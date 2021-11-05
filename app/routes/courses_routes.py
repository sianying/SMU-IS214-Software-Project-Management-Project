from flask import request
from . import routes
from .utility import *
from modules.course_manager import CourseDAO
from modules.staff_manager import StaffDAO
from modules.trainer_manager import TrainerDAO

# ============= Read ===================
@routes.route('/courses')
def retrieve_all_courses():
    course_dao = CourseDAO()
    course_list = course_dao.retrieve_all()
    if len(course_list):
        return format_response(200, [course.json() for course in course_list])
    
    return format_response(404, "No courses found")

@routes.route("/courses/eligible/<string:staff_id>")
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

@routes.route("/courses/<string:course_id>")
def retrieve_specific_course(course_id):
    course_dao = CourseDAO()
    course = course_dao.retrieve_one(course_id)

    if course != None:
        return format_response(200, course.json())

    return format_response(404, "No course found with id "+course_id)

# retrieve those that can teach a course, not those that are currently teaching the course.
# for HR
@routes.route("/courses/qualified/<string:course_id>")
def retrieve_qualified_trainers(course_id):
    trainer_dao = TrainerDAO()
    trainer_list = trainer_dao.retrieve_qualified_trainers(course_id)
    if len(trainer_list):
        return format_response(200, [trainerObj.json() for trainerObj in trainer_list])
    
    return format_response(404, "No trainer found.")

# retrieve all the courses that a trainer is actually teaching.
# class_list is filtered to only include classes that the trainer is teaching.
# for Trainer
@routes.route("/courses/assigned/<string:staff_id>")
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

@routes.route('/courses/enrolled/<string:staff_id>')
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

# ============= Create ==================
@routes.route("/courses", methods =['POST'])
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