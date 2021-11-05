from flask import request
from . import routes
from .utility import *
from modules.section_manager import SectionDAO
from modules.class_manager import ClassDAO

# ============= Read ===================

@routes.route("/section/<string:course_id>/<int:class_id>")
def retrieve_all_section_from_class(course_id, class_id):
    section_dao = SectionDAO()
    section_list = section_dao.retrieve_all_from_class(course_id, class_id)
    if len(section_list):
        return format_response(200, [sectionObj.json() for sectionObj in section_list])
    
    return format_response(404, "No section found for Course {}, Class {}".format(course_id, class_id))

@routes.route("/section/<string:section_id>")
def retrieve_specific_section(section_id):
    section_dao = SectionDAO()
    section = section_dao.retrieve_one(section_id)

    if section != None:
        return format_response(200, section.json())

    return format_response(404, "No section found with id "+section_id)

# ============= Create ==================

@routes.route("/section", methods=['POST'])
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

