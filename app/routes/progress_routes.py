from flask import request
from . import routes
from .utility import *
from modules.progress_manager import ProgressDAO
# ============= Read ===================
@routes.route("/progress/<string:staff_id>/<string:course_id>")
def check_learner_progress(staff_id, course_id):
    progress_dao = ProgressDAO()
    progressObj = progress_dao.retrieve_by_learner_and_course(staff_id, course_id)

    if progressObj:
        return format_response(200, progressObj.json())
    
    return format_response(404, "Could not find any progress for staff {} and course {}".format(staff_id, course_id))
