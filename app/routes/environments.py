from crypt import methods
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import get_project_id, create_slug,get_current_user
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
        if has_access_to_project(project_id,user.id):
            if id==0:
                environments = EnvModel.get_all_envs(project_id)
                return jsonify({"environments": environments}), 200
            environment = EnvModel.get_one_env(id)
            return jsonify(environment), 200
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to access the project components"})
    except Exception as e:
        return jsonify(str(e)), 400


@env_blueprint.route('/new', methods=['POST'])
@jwt_required()
def createEnv():
    req_data = request.json
    req_data['project'] = get_project_id(req_data.get("project"))
    req_data['name'] = create_slug(req_data.get("name"))
    user = get_current_user()
    req_data['created_by'] = user.id
    req_data['modified_by'] = user.id
    if has_access_to_project(req_data['project'],user.id):
        try:
            data = env_schema.load(req_data)
        except ValidationError as err:
            return jsonify(str(err)), 400
        
        is_exist = EnvModel.is_exist(data['name'], data['project'])

        if is_exist:
            return jsonify({"error": "You already have a environments of the same name in this project."}), 400

        env = EnvModel(data)
        env.save()
        return jsonify({"success" : "Environment created successfully!"})
    else:
        return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"})

@env_blueprint.route('/delete',methods=["POST"])
@jwt_required()
def delete_env():
    req_data = request.json
    user = get_current_user()
    try:
        environment = EnvModel.query.get(req_data.get('env'))
    except Exception as err:
        return jsonify(str(err))
    if environment:
        if has_access_to_project(environment.project,user.id):
            environment.delete()
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make deletions in the project components"})
    else:
        return jsonify({"error" : "No such environment exists"})
    return jsonify({"Success" : "Environment deleted successfully"})

@env_blueprint.route('/update',methods=["POST"])
@jwt_required()
def update_env():
    req_data = request.json
    user = get_current_user()
    try:
        environment = req_data.get('id')
        environment = EnvModel.query.get(environment)
        if environment:
            if has_access_to_project(environment.project,user.id):
                if req_data.get('name'):
                    name = req_data.get('name')
                    environment.name = name
                if req_data.get('url'):
                    url = req_data.get('url')
                    environment.url = url
                environment.update({'modified_by' : user.id})
            else:
                return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"})
        else:
            return jsonify({"error" : "No such environment exists"})
    except Exception as err:
        return jsonify(str(err))
    return jsonify({"success" : "Environment updated successfully!"})
