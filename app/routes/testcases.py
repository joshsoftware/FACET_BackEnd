from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from app.helpers import create_slug, get_project_id
from app.models.TestcaseModel import TestcaseModel, TestcaseSchema

testcases_blueprint = Blueprint('testcases', __name__)
testcase_schema = TestcaseSchema()

@testcases_blueprint.route('/', methods=['GET'])
@testcases_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def get_testcases(id=0):
    try:
        project_id = get_project_id(request.args.get("project"))
        if id!=0:
            data = TestcaseModel.get_one_testcase(id)
            return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

        data = TestcaseModel.get_all_testcases(project_id)
        return jsonify({"testcases": data}), 200, {"content-type": "application/json; charset=UTF-8"}
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
        del req_data['project']
        
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
    except Exception as e:
        return jsonify(str(e)), 400

@testcases_blueprint.route('/delete',methods=["POST"])
@jwt_required()
def delete_testcase():
    req_data = request.json
    try:
        testcase = TestcaseModel.query.get(req_data.get('testcase'))
    except Exception as e:
        return jsonify(str(e))
    if testcase:
        testcase.delete()
    else:
        return jsonify({"error" : "No such testcase exists"})
    return jsonify({"Success" : "testcase deleted successfully"})
