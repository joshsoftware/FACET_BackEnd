import json
from flask import Blueprint, jsonify, request
from api_testing_tool import db
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool.helpers.utils import create_id

testcases_blueprint = Blueprint('testcases', __name__)

@testcases_blueprint.route('/api/testcases')
@jwt_required()
def get_testcases():
    data = request.json

    project_id = data.get('project_id')

    testcases = db.testcases.find({"project":project_id})

    return jsonify(list(testcases))



@testcases_blueprint.route('/api/create-testcase', methods=['POST'])
@jwt_required()
def create_testcase():
    data = request.json

    project_id = data.get('project_id')
    endpoint_id = data.get('endpoint_id')
    title = data.get('title')
    method = data.get('method')
    payload_id = data.get('payload_id')

    if project_id=="" or endpoint_id=="" or title=="" or len(method)<3 or payload_id=="":
        return jsonify({"errors":"All fields are Required!"})

    db.testcases.insert_one({
        "_id":create_id(),
        "project": project_id,
        "endpoint": db.endpoints.find_one({"_id":endpoint_id}),
        "title": title,
        "method": method,
        "payload": db.payloads.find_one({"_id":payload_id})
    })

    return jsonify({"msg": "Testcase created Successfully!!"})
