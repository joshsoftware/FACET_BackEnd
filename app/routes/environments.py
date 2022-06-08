from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import get_project_id, create_slug
from app.models.EnvModel import EnvModel, EnvSchema

env_blueprint = Blueprint('environments', __name__)
env_schema = EnvSchema()

@env_blueprint.route('', methods=['GET'])
@env_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def getEnvs(id=0):
    try:
        project_id = get_project_id(request.args.get('project'))
        if id==0:
            environments = EnvModel.get_all_envs(project_id)
            return jsonify({"environments": environments}), 200
        environment = EnvModel.get_one_env(id)
        return jsonify(environment), 200
    except Exception as e:
        return jsonify(str(e)), 400


@env_blueprint.route('/new', methods=['POST'])
@jwt_required()
def createEnv():
    req_data = request.json
    req_data['project'] = get_project_id(req_data.get("project"))
    req_data['name'] = create_slug(req_data.get("name"))
    
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

@env_blueprint.route('/delete',methods=["POST"])
@jwt_required()
def delete_env():
    req_data = request.json
    try:
        environment = EnvModel.query.get(req_data.get('env'))
    except Exception as e:
        return jsonify(str(e))
    if environment:
        environment.delete()
    else:
        return jsonify({"error" : "No such environment exists"})
    return jsonify({"Success" : "Environment deleted successfully"})
