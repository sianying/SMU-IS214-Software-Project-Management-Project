from flask import request
from . import routes
from .utility import *
from modules.quiz_manager import QuizDAO
from modules.class_manager import ClassDAO
from modules.section_manager import SectionDAO
from modules.attempt_manager import AttemptDAO

# ============= Read ===================
@routes.route("/quiz/<string:quiz_id>")
def retrieve_quiz_by_ID(quiz_id):
    quiz_dao = QuizDAO()
    quizObj = quiz_dao.retrieve_one(quiz_id)

    if quizObj:
        return format_response(200, quizObj.json())
    
    return format_response(404, "No quiz was found with id "+quiz_id)

@routes.route("/quiz/section/<string:section_id>")
def retrieve_quiz_by_section(section_id):
    quiz_dao = QuizDAO()
    quizObj = quiz_dao.retrieve_by_section(section_id)

    if quizObj:
        return format_response(200, quizObj.json())
    
    return format_response(404, "No quiz was found for section "+ section_id)

# ============= Create ==================

@routes.route("/quiz/create", methods=['POST'])
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

# ============= Update ==================
@routes.route("/quiz/update", methods=['PUT'])
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

