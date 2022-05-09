from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from jsonschema import ValidationError, validate
from api_testing_tool import db
from api_testing_tool.helpers import validation_error, create_slug, get_project_id
from api_testing_tool.schema import testdata_schema

testdata_blueprint = Blueprint('testdata', __name__)

@testdata_blueprint.route("/api/testdata",methods = ["GET"])
@jwt_required()
def getTestdata():
    project = get_project_id(request.args.get('project'))
    testdata = db.testdata.find({"project" : project})
    return jsonify({"testdata":list(testdata)})

@testdata_blueprint.route("/api/testdata/new",methods = ["POST"])
@jwt_required()
def createTestdata():
    data = request.json
    testcase_id = data.get("testcase_id")
    payload = data.get("payload")
    expected_outcome = data.get("expected_outcome")
    name = create_slug(data.get("name"))
    
    try:
        validate(data, testdata_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    testdata = {
        "name" : name,
        "payload" : payload,
        "expected_outcome": expected_outcome
    }
    
    # if testdata:
    testcase = db.testcases.find_one({"_id": testcase_id})
    testcase['testdata'].append(testdata)
    if testcase:
        if not db.testcases.find_one({"_id": testcase_id, "testdata.name": name}):
            db.testcases.update_one({"_id": testcase_id}, {"$set": {"testdata": testcase['testdata']}})
        else:
            return jsonify({"errors": f"testdata {name} already exist"})
    return jsonify({"success" : "testdata added successfully"})