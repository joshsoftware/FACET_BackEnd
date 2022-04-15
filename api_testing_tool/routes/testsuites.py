from flask import Blueprint,jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from jsonschema import ValidationError, validate
from api_testing_tool import db
from api_testing_tool.helpers import create_id, validation_error,create_slug, get_project_id
from api_testing_tool.schema import testsuite_schema

testsuite_blueprint = Blueprint('testsuites', __name__)

@testsuite_blueprint.route('/api/testsuites',methods = ["GET"])
@jwt_required()
def getTestsuites():
    try:
        project_id = get_project_id(request.args.get("project"))
        project_testsuites = db.testsuite.find({"project" : project_id})
        return jsonify({"testsuites" : list(project_testsuites)})
    except Exception as e:
        return jsonify(e),400
    
@testsuite_blueprint.route('/api/testsuite/<string:id>', methods=['GET'])
@jwt_required()
def getTestsuite(id):
    testsuite = db.testsuite.find_one({"_id":id})
    
    testcases = []
    for i in testsuite['testcases']:
        testcase = db.testcases.find_one({"_id":i})
        testcase['endpoint'] = db.endpoints.find_one({"_id": testcase['endpoint']})
        testcase['header'] = db.headers.find_one({"_id": testcase['header']})
        testcase['payload'] = db.payloads.find_one({"_id": testcase['payload']})
        testcase['testdata'] = list(db.testdata.find({"testcase_id":i})) or None
        testcases.append(testcase)
    
    testsuite['testcases'] = testcases

    return jsonify(testsuite)

@testsuite_blueprint.route('/api/create-testsuite',methods = ["POST"])
@jwt_required()
def createTestsuites():
    data = request.json 
    project_id = data.get("project_id")
    name = create_slug(data.get("name"))
    description = data.get("description")
    array_of_testcases = data.get("testcases")

    try:
        validate(data, testsuite_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    if db.testsuite.find_one({"project_id": project_id, "name" : name}) == None:
        db.testsuite.insert_one({
            "_id" : create_id(),
            "project" : project_id,
            "user": get_current_user()['_id'],
            "name" : name,
            "description" : description,
            "testcases" : array_of_testcases
        })
        return jsonify({"success" : "testsuite created with the given testcases"})
    else:
        return jsonify({"error" : "Invalid details"})
