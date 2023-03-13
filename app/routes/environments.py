from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import get_project_id, create_slug, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.EnvModel import EnvModel, EnvSchema
import logging

env_blueprint = Blueprint('environments', __name__)
env_schema = EnvSchema()


@env_blueprint.route('', methods=['GET'])
@env_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def getEnvs(id=0):
    try:
        user = get_current_user()
        project_id = get_project_id(request.args.get('project'),user.user_organization)
        logging.info(f"GET request to fetch environments by {user.id} with params:{dict(request.args)} and url:{request.url}")
        if not has_access_to_project(project_id, user.id):
            logging.info(f"GET request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id == 0:
            environments = EnvModel.get_all_envs(project_id)
            logging.info(f"GET request successful, environments returned successfully for project id:{project_id}")
            return jsonify({"environments": environments}), 200

        environment = EnvModel.get_one_env(id)
        logging.info(f"GET request successful, environments returned successfully for environment id:{id}")
        return jsonify(environment), 200
    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@env_blueprint.route('', methods=['POST'])
@jwt_required()
def createEnv():
    try:
        user = get_current_user()
        req_data = request.json
        req_data['project'] = get_project_id(create_slug(req_data.get("project")),user.user_organization)
        req_data['name'] = create_slug(req_data.get("name"))
        logging.info(f"POST request to create environmet by user:{user.id} with payload:{req_data}")
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        if not has_access_to_project(req_data['project'], user.id):
            logging.info(f"POST request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        try:
            data = env_schema.load(req_data)
        except ValidationError as err:
            logging.error(f"environment creation failed due to the following error {err}")
            return jsonify({"error": str(err)}), 400

        is_exist = EnvModel.is_exist(data['name'], data['project'])

        if is_exist:
            logging.info(f"environment creation failed due to duplicate entry")
            return jsonify({"error": "You already have a environments of the same name in this project."}), 400

        env = EnvModel(data)
        env.save()
        logging.info(f"environment created successfully")
        return jsonify({"message": "Environment created successfully!"}), 201
    except Exception as err:
        logging.exception(f"POST request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}),400


@env_blueprint.route('', methods=["DELETE"])
@jwt_required()
def delete_env():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"DELETE request to delete environment by user:{user.id} with payload:{req_data}")
        try:
            environment = EnvModel.query.get(req_data.get('env'))
        except Exception as err:
            logging.exception(f"DELETE request failed due to the following error:{err}")
            return jsonify({"error": "something went wrong"}), 400

        if not environment:
            logging.info(f"DELETE request failed as no such environment exists for the project")
            return jsonify({"error": "No such environment exists"}), 404

        if not has_access_to_project(environment.project, user.id):
            logging.info(f"DELETE request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401
        environment.delete()
        logging.info(f"environment deleted sucessfully")
        return jsonify({"message": "Environment deleted successfully"}), 200
    except Exception as err:
        logging.exception(f"DELETE request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}), 400


@env_blueprint.route('', methods=["PUT"])
@jwt_required()
def update_env():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"PUT request to update environment by user:{user.id} with payload:{req_data}")
        environment = req_data.get('id')
        environment = EnvModel.query.get(environment)
        if not environment:
            logging.info(f"PUT request failed as no such environments exists for the project")
            return jsonify({"error": "No such environment exists"}), 404

        if not has_access_to_project(environment.project, user.id):
            logging.info(f"PUT request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        environment.name = req_data.get('name') if req_data.get('name') else environment.name

        environment.url = req_data.get('url') if req_data.get('url') else environment.url

        environment.update({'modified_by': user.id})
        logging.info(f"environment updated sucessfully")
        return jsonify({"message": "Environment updated successfully!"}), 200

    except Exception as err:
        logging.exception(f"PUT request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400
