from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from api_testing_tool import db
from api_testing_tool.helpers.utils import create_id

testsuite_blueprint = Blueprint('testsuites', __name__)

@testsuite_blueprint.route('/api/get-testsuites',methods = ["GET"])
@jwt_required()
def getTestsuite():
    data = request.json 
    project_id = data.get("project_id")
    project_testsuites = db.testsuite.find({"project_id" : project_id})
    return jsonify({"testsuites" : list(project_testsuites)})

@testsuite_blueprint.route('/api/create-testsuites',methods = ["POST"])
@jwt_required()
def createTestsuites():
    data = request.json 
    project_id = data.get("project_id")
    title = data.get("title")
    description = data.get("description")
    array_of_testcases = data.get("testcases")
    if db.testsuite.find_one({"project_id": project_id,"title" : title}) == None:
        db.testsuite.insert_one({
            "_id" : create_id(),
            "project_id" : project_id,
            "title" : title,
            "description" : description,
            "testcases" : array_of_testcases
        })
        return jsonify({"success" : "testsuite created with the given testcases"})
    else:
        return jsonify({"error" : "Invalid details"})
