from flask import request
from . import routes
from .utility import *
from .classes_routes import enroll_learners
from modules.staff_manager import StaffDAO
from modules.request_manager import RequestDAO, Request
from modules.class_manager import ClassDAO

# ============= Read ===================
@routes.route("/request")
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

@routes.route("/request/<string:staff_id>")
def retrieve_all_request_by_staff(staff_id):
    request_dao = RequestDAO()
    request_list = request_dao.retrieve_all_from_staff(staff_id)

    if len(request_list):
        return format_response(200, [requestObj.json() for requestObj in request_list])
    
    return format_response(404, "No requests found")

# ============= Create ==================
@routes.route("/request", methods =['POST'])
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

@routes.route("/request/update", methods = ['PUT'])
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
