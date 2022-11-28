from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from jsonschema import ValidationError
from app.helpers import create_slug, get_project_id, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.HeaderModel import HeaderModel, HeaderSchema
import logging

headers_blueprint = Blueprint('headers', __name__)
header_schema = HeaderSchema()


@headers_blueprint.route('/', methods=["GET"])
@headers_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getHeaders(id=0):
    try:
        user = get_current_user()
        project_id = get_project_id(request.args.get("project"))
        logging.info(f"GET request to fetch header by user:{user.id} with params:{dict(request.args)} and url:{request.url}")
        if not has_access_to_project(project_id, user.id):
            logging.info(f"GET request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id == 0:
            data = HeaderModel.get_all_headers(project_id)
            logging.info(f"GET request successfull, headers returned successfully for project id:{project_id}")
            return jsonify({"headers": data}), 200

        data = HeaderModel.get_one_header(id)
        logging.info(f"GET request successfull, header returned successfully for header id:{id}")
        return jsonify(data), 200
    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@headers_blueprint.route('/new', methods=["POST"])
@jwt_required()
def createHeaders():
    try:
        req_data = request.json
        req_data['name'] = create_slug(req_data.get('name'))
        req_data['project'] = get_project_id(req_data.get('project'))
        user = get_current_user()
        logging.info(f"POST request to create header by user:{user.id} with payload:{req_data}")
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        if not has_access_to_project(req_data['project'], user.id):
            logging.info(f"POST request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        try:
            data = header_schema.load(req_data)
        except ValidationError as err:
            logging.error(f"header creation failed due to the following error {err}")
            return jsonify({"error": str(err)}), 400

        is_exist = HeaderModel.is_exist(data.get('name'), data.get('project'))

        if is_exist:
            logging.info(f"header creation failed due to duplicate entry")
            return jsonify({"error": "You already have a header of the same name in this project."}), 400

        header = HeaderModel(data)
        header.save()
        logging.info(f"header created successfully")
        return jsonify({"message": "Header created successfully!"}), 201
    except Exception as err:
        logging.exception(f"POST request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}),400


@headers_blueprint.route('/delete/', methods=["DELETE"])
@jwt_required()
def delete_header():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"DELETE request to delete header by user:{user.id} with payload:{req_data}")
        try:
            header = HeaderModel.query.get(req_data.get('header'))
        except Exception as err:
            logging.exception(f"DELETE request failed due to the following error:{err}")
            return jsonify({"error": "something went wrong"}), 400

        if not header:
            logging.info(f"DELETE request failed as no such header exists for the project")
            return jsonify({"error": "No such header exists"}), 404

        if not has_access_to_project(header.project, user.id):
            logging.info(f"DELETE request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401

        header.delete()
        logging.info(f"header deleted sucessfully")
        return jsonify({"message": "Header deleted successfully"}), 200
    except Exception as err:
        logging.exception(f"DELETE request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}),400

@headers_blueprint.route('/update', methods=["PUT"])
@jwt_required()
def update_header():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"PUT request to update header by user:{user.id} with payload:{req_data}")
        header = req_data.get('id')
        header = HeaderModel.query.get(header)
        if not header:
            logging.info(f"PUT request failed as no such header exists for the project")
            return jsonify({"error": "No such header exists"}), 404

        if not has_access_to_project(header.project, user.id):
            logging.info(f"PUT request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        header.name = req_data.get('name') if req_data.get('name') else header.name
        
        header.header  = req_data.get('header') if type(req_data.get('header')) is dict else header.header
         
        header.update({'modified_by': user.id})
        logging.info(f"header updated sucessfully")
        return jsonify({"message": "Header updated successfully"}), 200
    except Exception as err:
        logging.exception(f"PUT request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400
