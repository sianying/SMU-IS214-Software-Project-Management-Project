from flask import jsonify

def format_response(code, data):
    return jsonify(
        {
            "code": code,
            "data": data
        }
    ), code