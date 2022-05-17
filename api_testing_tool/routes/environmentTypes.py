from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from jsonschema import ValidationError, validate
from api_testing_tool import db
from api_testing_tool.helpers import get_project_id, create_id, create_slug, validation_error
from api_testing_tool.schema import environments_schema

envTypes_blueprint = Blueprint('environmentTypes', __name__)

@envTypes_blueprint.route('/api/environments', methods=['GET'])
@envTypes_blueprint.route('/api/environments/<string:id>', methods=['GET'])
@jwt_required()
def getEnvTypes(id=0):
    try:
        project_id = get_project_id(request.args.get("project"))
        if id==0:
            envTypes = db.envtypes.find({"project": project_id, "user": get_current_user()['_id']}, {"project": 0, "user": 0})
            return jsonify({"environments": list(envTypes)}), 200
        envTypes = db.envtypes.find_one({"_id": id, "user": get_current_user()['_id']}, {"project":0, "user": 0})
        return jsonify(envTypes), 200
    except Exception as e:
        return jsonify(e), 400
    
@envTypes_blueprint.route('/api/environments/new', methods=['POST'])
@jwt_required()
def createEnvTypes():
    data = request.json
    name = create_slug(data.get("name"))
    project = get_project_id(data.get("project"))
    user = get_current_user()['_id']

    try:
        validate(data, environments_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    if db.envtypes.find_one({"name": name, "project": project, "user": user}):
        return jsonify({"errors": "You already have a environment of the same name"}), 400

    db.envtypes.insert_one({
        "_id": create_id(),
        **data,
        "project": project,
        "name": name,
        "user": user
    })

    return jsonify({"success": "Environment Added Successfully!"}), 200