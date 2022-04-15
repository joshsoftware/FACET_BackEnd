from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate
from api_testing_tool import db
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool.helpers import create_id, validation_error,create_slug
from api_testing_tool.schema import testcase_schema

testcases_blueprint = Blueprint('testcases', __name__)

@testcases_blueprint.route('/api/testcases')
@jwt_required()
def get_testcases():
    data = request.json

    project_id = get_project_id(data.get("name"))

    testcases = db.testcases.find({"project":project_id})

    return jsonify(list(testcases))



@testcases_blueprint.route('/api/create-testcase', methods=['POST'])
@jwt_required()
def create_testcase():
    data = request.json

    project_id = data.get('project_id')
    endpoint_id = data.get('endpoint_id')
    name = create_slug(data.get('name'))
    method = data.get('method')
    payload_id = data.get('payload_id')
    header_id = data.get('header_id')

    try:
        validate(data, testcase_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    db.testcases.insert_one({
        "_id":create_id(),
        "project": project_id,
        "endpoint": endpoint_id,
        "name": name,
        "method": method,
        "payload": payload_id,
        "header": header_id,
        "testdata": None,
        "user": get_current_user()['_id']
    })

    return jsonify({"msg": "Testcase created Successfully!!"})
