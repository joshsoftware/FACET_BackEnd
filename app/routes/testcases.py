from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from app.helpers import create_slug, get_project_id,get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TestcaseModel import TestcaseModel, TestcaseSchema

testcases_blueprint = Blueprint('testcases', __name__)
testcase_schema = TestcaseSchema()

@testcases_blueprint.route('/', methods=['GET'])
@testcases_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def get_testcases(id=0):
    try:
        project_id = get_project_id(request.args.get("project"))
        user = get_current_user()
        if has_access_to_project(project_id,user.id):
            if id!=0:
                data = TestcaseModel.get_one_testcase(id)
                return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

            data = TestcaseModel.get_all_testcases(project_id)
            return jsonify({"testcases": data}), 200, {"content-type": "application/json; charset=UTF-8"}
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to access the project components"}),401
    except Exception as e:
        return jsonify(str(e)), 400



@testcases_blueprint.route('/new', methods=['POST'])
@jwt_required()
def create_testcase():
    """
    Accepts project, endpoint_id, payload_id, header_id, name, method as inputs
    """
    try:
        req_data = request.json
        req_data['name'] = create_slug(req_data.get('name'))
        req_data['project_id'] = get_project_id(req_data.get('project'))
        user = get_current_user()
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        del req_data['project']
        if has_access_to_project(req_data['project_id'],user.id):
            try:
                data = testcase_schema.load(req_data)
            except ValidationError as err:
                return jsonify(str(err)), 400

            is_exist = TestcaseModel.is_exist(data.get('name'), data.get('project_id'))

            if is_exist:
                return jsonify({"error": "You already have a testcases of the same name in this project."}), 400

            testcase = TestcaseModel(data)
            testcase.save()
            return jsonify({"success": "Testcase created successfully!"}), 201
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"}),401
    except Exception as e:
        return jsonify(str(e)), 400

@testcases_blueprint.route('/delete',methods=["POST"])
@jwt_required()
def delete_testcase():
    req_data = request.json
    user = get_current_user()
    try:
        testcase = TestcaseModel.query.get(req_data.get('testcase'))
    except Exception as e:
        return jsonify(str(e)),400
    if testcase:
        if has_access_to_project(testcase.project_id,user.id):
            testcase.delete()
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}),401
    else:
        return jsonify({"error" : "No such testcase exists"}),404
    return jsonify({"Success" : "testcase deleted successfully"}),200

@testcases_blueprint.route('/update',methods=["POST"])
@jwt_required()
def update_testcase():
    req_data = request.json
    user = get_current_user()
    try:
        testcase = req_data.get('id')
        testcase = TestcaseModel.query.get(testcase)
        if testcase:
            if has_access_to_project(testcase.project_id,user.id):
                if req_data.get('name'):
                    name = req_data.get('name')
                    testcase.name = name
                if req_data.get('method'):
                    method = req_data.get('method')
                    testcase.method = method
                if req_data.get('endpoint'):
                    endpoint = req_data.get('endpoint')
                    testcase.endpoint_id = endpoint
                if req_data.get('header'):
                    header = req_data.get('header')
                    testcase.header_id = header
                if req_data.get('payload'):
                    payload = req_data.get('payload')
                    testcase.payload_id = payload
                testcase.update({'modified_by' : user.id})
            else:
                return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"}),401
        else:
            return jsonify({"Error" : "No such Testcase exists"}),404
    except Exception as err:
        return jsonify(str(err)),400
    return jsonify({"Success" : "Testcase Updated successfully"}),200
