from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import get_project_id, create_slug, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.EnvModel import EnvModel, EnvSchema

env_blueprint = Blueprint('environments', __name__)
env_schema = EnvSchema()


@env_blueprint.route('', methods=['GET'])
@env_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def getEnvs(id=0):
    try:
        user = get_current_user()
        project_id = get_project_id(request.args.get('project'))
        if not has_access_to_project(project_id, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id == 0:
            environments = EnvModel.get_all_envs(project_id)
            return jsonify({"environments": environments}), 200

        environment = EnvModel.get_one_env(id)
        return jsonify(environment), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@env_blueprint.route('/new', methods=['POST'])
@jwt_required()
def createEnv():
    try:
        req_data = request.json
        req_data['project'] = get_project_id(create_slug(req_data.get("project")))
        req_data['name'] = create_slug(req_data.get("name"))
        user = get_current_user()
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        if not has_access_to_project(req_data['project'], user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        try:
            data = env_schema.load(req_data)
        except ValidationError as err:
            return jsonify({"error": str(err)}), 400

        is_exist = EnvModel.is_exist(data['name'], data['project'])

        if is_exist:
            return jsonify({"error": "You already have a environments of the same name in this project."}), 400

        env = EnvModel(data)
        env.save()
        return jsonify({"message": "Environment created successfully!"}), 201
    except Exception as err:
        print(str(err))
        return jsonify({"error":"something went wrong"}),400


@env_blueprint.route('/delete/', methods=["DELETE"])
@jwt_required()
def delete_env():
    try:
        req_data = request.json
        user = get_current_user()
        try:
            environment = EnvModel.query.get(req_data.get('env'))
        except Exception as err:
            print(str(err))
            return jsonify({"error": "something went wrong"}), 400

        if not environment:
            return jsonify({"error": "No such environment exists"}), 404

        if not has_access_to_project(environment.project, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401
        environment.delete()
        return jsonify({"message": "Environment deleted successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error":"something went wrong"}), 400


@env_blueprint.route('/update', methods=["PUT"])
@jwt_required()
def update_env():
    try:
        req_data = request.json
        user = get_current_user()
        environment = req_data.get('id')
        environment = EnvModel.query.get(environment)
        if not environment:
            return jsonify({"error": "No such environment exists"}), 404

        if not has_access_to_project(environment.project, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        environment.name = req_data.get('name') if req_data.get('name') else environment.name

        environment.url = req_data.get('url') if req_data.get('url') else environment.url

        environment.update({'modified_by': user.id})
        return jsonify({"message": "Environment updated successfully!"}), 200

    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400
