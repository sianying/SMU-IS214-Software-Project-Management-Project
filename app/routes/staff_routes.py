from flask import request
from . import routes
from .utility import *
from modules.course_manager import CourseDAO
from modules.staff_manager import StaffDAO

# ============= Read ===================

@routes.route("/staff/<string:staff_id>")
def retrieve_specific_staff(staff_id):
    staff_dao = StaffDAO()
    staffObj = staff_dao.retrieve_one(staff_id)
    if staffObj != None:
        return format_response(200, staffObj.json())
    return format_response(404,"No staff found with staff_id "+ staff_id)


@routes.route("/staff/eligible/<string:course_id>")
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


