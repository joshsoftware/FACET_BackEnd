from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from app.helpers import create_slug, get_project_id, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TeststepModel import TestStepModel, TeststepSchema
import logging

teststeps_blueprint = Blueprint('teststeps', __name__)
teststep_schema = TeststepSchema()


@teststeps_blueprint.route('/', methods=['GET'])
@teststeps_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def get_teststeps(id=0):
    try:
        project_id = get_project_id(request.args.get("project"))
        user = get_current_user()
        logging.info(f"GET request to fetch teststep by user:{user.id} with params:{dict(request.args)} and url:{request.url}")
        if not has_access_to_project(project_id, user.id):
            logging.info(f"GET request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id != 0:
            data = TestStepModel.get_one_teststep(id)
            logging.info(f"GET request successfull, teststep returned successfully for teststep id:{id}")
            return jsonify(data), 200

        data = TestStepModel.get_all_teststeps(project_id)
        logging.info(f"GET request successfull, teststeps returned successfully for project id:{project_id}")
        return jsonify({"teststeps": data}), 200
    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@teststeps_blueprint.route('/new', methods=['POST'])
@jwt_required()
def create_teststep():
    """
    Accepts project, endpoint_id
, payload_id, header_id, name, method as inputs
    """
    try:
        req_data = request.json
        req_data['name'] = create_slug(req_data.get('name'))
        req_data['project_id'] = get_project_id(req_data.get('project'))
        user = get_current_user()
        logging.info(f"POST request to create teststep by user:{user.id} with payload:{req_data}")
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        del req_data['project']
        if not has_access_to_project(req_data['project_id'], user.id):
            logging.info(f"POST request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        try:
            data = teststep_schema.load(req_data)
        except ValidationError as err:
            logging.error(f"teststep creation failed due to the following error {err}")
            return jsonify({"error": str(err)}), 400

        is_exist = TestStepModel.is_exist(
            data.get('name'), data.get('project_id'))

        if is_exist:
            logging.info(f"teststep creation failed due to duplicate entry")
            return jsonify({"error": "You already have a teststeps of the same name in this project."}), 400

        teststep = TestStepModel(data)
        teststep.save()
        logging.info(f"teststep created successfully")
        return jsonify({"message": "Teststep created successfully!"}), 201
    except Exception as err:
        logging.exception(f"POST request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@teststeps_blueprint.route('/delete/', methods=["DELETE"])
@jwt_required()
def delete_teststep():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"DELETE request to delete teststep by user:{user.id} with payload:{req_data}")
        try:
            teststep = TestStepModel.query.get(req_data.get('teststep'))
        except Exception as err:
            logging.exception(f"DELETE request failed due to the following error:{err}")
            return jsonify({"error": "something went wrong"}), 400

        if not teststep:
            logging.info(f"DELETE request failed as no such teststep exists for the project")
            return jsonify({"error": "No such teststep exists"}), 404

        if not has_access_to_project(teststep.project_id, user.id):
            logging.info(f"DELETE request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401

        teststep.delete()
        logging.info(f"teststep deleted sucessfully")
        return jsonify({"message": "teststep deleted successfully"}), 200
    except Exception as err:
        logging.exception(f"DELETE request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@teststeps_blueprint.route('/update', methods=["PUT"])
@jwt_required()
def update_teststep():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"PUT request to update teststep by user:{user.id} with payload:{req_data}")
        teststep = req_data.get('id')
        teststep = TestStepModel.query.get(teststep)
        if not teststep:
            logging.info(f"PUT request failed as no such teststep exists for the project")
            return jsonify({"error": "No such Teststep exists"}), 404

        if not has_access_to_project(teststep.project_id, user.id):
            logging.info(f"PUT request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        teststep.name = req_data.get('name') if req_data.get('name') else teststep.name
        
        teststep.method  = req_data.get('method') if req_data.get('method') else teststep.method

        teststep.endpoint_id = req_data.get('endpoint_id') if req_data.get('endpoint_id') else teststep.endpoint

        teststep.header_id = req_data.get('header_id') if req_data.get('header_id') else teststep.header
        
        teststep.payload_id = req_data.get('payload_id') if req_data.get('payload_id') else teststep.payload

        teststep.update({'modified_by': user.id})
        logging.info(f"teststep updated sucessfully")
        return jsonify({"message": "Teststep Updated successfully"}), 200
    except Exception as err:
        logging.exception(f"PUT request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400
