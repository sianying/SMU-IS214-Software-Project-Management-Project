from flask import Flask, request, json
from flask_cors import CORS
import boto3
import os
import re
from botocore.errorfactory import ClientError
from decimal import Decimal
from modules.section_manager import SectionDAO, Material
from routes import *
from routes.utility import format_response

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

# register all the routes in the routes folder
app.register_blueprint(routes)


# These 2 routes require session from the utility methods
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
        mat = Material(data)
    except:
        return format_response(400, "Not proper request body.")
    
    section.add_material(mat)
    
    try:
        section_dao.update_section(section)
        return format_response(201, mat.json())
    except Exception as e:
        return format_response(500, "An error occurred when updating section object.")

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug= True)