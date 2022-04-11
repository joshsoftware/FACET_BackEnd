from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from jsonschema import ValidationError, validate
from api_testing_tool import db
from api_testing_tool.helpers import create_id, validation_error
from api_testing_tool.helpers.utils import create_slug
from api_testing_tool.schema import testdata_schema

testdata_blueprint = Blueprint('testdata', __name__)

@testdata_blueprint.route("/api/get_testdata",methods = ["GET"])
@jwt_required()
def getTestdata():
    data = request.json
    testcase_id = data.get("testcase_id")
    testcase_testdata = db.testdata.find({"testcase_id" : testcase_id})
    return jsonify(testcase_testdata)

@testdata_blueprint.route("/api/create-testdata",methods = ["POST"])
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

    db.testdata.insert_one({
        "_id" : create_id(),
        "name" : name,
        "testcase_id" : testcase_id,
        "payload" : payload,
        "expected_outcome": expected_outcome
    })
    return jsonify({"success" : "testdata added successfully"})