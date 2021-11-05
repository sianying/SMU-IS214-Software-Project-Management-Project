from flask import request
from . import routes
from .utility import *
from modules.attempt_manager import AttemptDAO
from modules.quiz_manager import QuizDAO
from modules.progress_manager import ProgressDAO

# ============= Read ===================
@routes.route("/attempts/<string:quiz_id>/<string:staff_id>")
def retrieve_quiz_attempts_by_learner(quiz_id, staff_id):
    attempt_dao = AttemptDAO()
    attempts_list = attempt_dao.retrieve_by_learner(quiz_id, staff_id)

    if len(attempts_list):
        return format_response(200, [attemptObj.json() for attemptObj in attempts_list])
    
    return format_response(404, "No attempts were found for Staff {} for Quiz {}".format(staff_id,quiz_id))

# ============= Create ==================
@routes.route("/attempts", methods=['POST'])
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
