from re import I
from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate
from api_testing_tool import db
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool.helpers import create_id, validation_error,create_slug, get_project_id
from api_testing_tool.schema import testcase_schema

testcases_blueprint = Blueprint('testcases', __name__)


def get_data_and_add_to_testcase(i):
    i['header'] = db.headers.find_one({"_id":i['header']}, {"user": 0, "project":0})
    i['endpoint'] = db.endpoints.find_one({"_id":i['endpoint']}, {"user": 0, "project":0})
    i['payload'] = db.payloads.find_one({"_id":i['payload']}, {"user": 0, "project":0})
    return i


@testcases_blueprint.route('/api/testcases', methods=['GET'])
@testcases_blueprint.route('/api/testcases/<string:id>', methods=['GET'])
@jwt_required()
def get_testcases(id=0):
    try:
        project_id = get_project_id(request.args.get("project"))
        if id==0:
            testcases = list(db.testcases.find({"project":project_id}, {"project": 0, "user": 0}))
            for i in testcases:
                i = get_data_and_add_to_testcase(i)

            return jsonify({"testcases": list(testcases)})
        
        testcase = get_data_and_add_to_testcase(db.testcases.find_one({"project":project_id, "_id":id}, {"project": 0, "user": 0}))
        return jsonify(testcase), 200
    except Exception as e:
        return jsonify(e), 400

@testcases_blueprint.route('/api/testcases/new', methods=['POST'])
@jwt_required()
def create_testcase():
    data = request.json

    project_id = get_project_id(data.get('project'))
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
        "testdata": [],
        "user": get_current_user()['_id']
    })

    return jsonify({"msg": "Testcase created Successfully!!"})
