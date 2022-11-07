from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from app.helpers import create_slug, get_project_id, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TeststepModel import TestStepModel, TeststepSchema

teststeps_blueprint = Blueprint('teststeps', __name__)
teststep_schema = TeststepSchema()


@teststeps_blueprint.route('/', methods=['GET'])
@teststeps_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def get_teststeps(id=0):
    try:
        project_id = get_project_id(request.args.get("project"))
        user = get_current_user()
        if not has_access_to_project(project_id, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id != 0:
            data = TestStepModel.get_one_teststep(id)
            return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

        data = TestStepModel.get_all_teststeps(project_id)
        return jsonify({"teststeps": data}), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@teststeps_blueprint.route('/new', methods=['POST'])
@jwt_required()
def create_teststep():
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
        if not has_access_to_project(req_data['project_id'], user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        try:
            data = teststep_schema.load(req_data)
        except ValidationError as err:
            return jsonify(str(err)), 400

        is_exist = TestStepModel.is_exist(
            data.get('name'), data.get('project_id'))

        if is_exist:
            return jsonify({"error": "You already have a teststeps of the same name in this project."}), 400

        teststep = TestStepModel(data)
        teststep.save()
        return jsonify({"message": "Teststep created successfully!"}), 201
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@teststeps_blueprint.route('/delete/', methods=["DELETE"])
@jwt_required()
def delete_teststep():
    req_data = request.json
    user = get_current_user()
    try:
        teststep = TestStepModel.query.get(req_data.get('teststep'))
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400

    if not teststep:
        return jsonify({"error": "No such teststep exists"}), 404

    if not has_access_to_project(teststep.project_id, user.id):
        return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401

    teststep.delete()
    return jsonify({"message": "teststep deleted successfully"}), 200


@teststeps_blueprint.route('/update', methods=["PUT"])
@jwt_required()
def update_teststep():
    req_data = request.json
    user = get_current_user()
    try:
        teststep = req_data.get('id')
        teststep = TestStepModel.query.get(teststep)
        if not teststep:
            return jsonify({"error": "No such Teststep exists"}), 404

        if not has_access_to_project(teststep.project_id, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        if req_data.get('name'):
            name = req_data.get('name')
            teststep.name = name

        if req_data.get('method'):
            method = req_data.get('method')
            teststep.method = method

        if req_data.get('endpoint_id'):
            endpoint = req_data.get('endpoint_id')
            teststep.endpoint_id = endpoint

        if req_data.get('header_id'):
            header = req_data.get('header_id')
            teststep.header_id = header

        if req_data.get('payload_id'):
            payload = req_data.get('payload_id')
            teststep.payload_id = payload

        teststep.update({'modified_by': user.id})
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400
    return jsonify({"message": "Teststep Updated successfully"}), 200
