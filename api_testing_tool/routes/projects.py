from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool import db
from api_testing_tool.helpers import create_slug, create_id, validation_error
from api_testing_tool.schema import projects_schema
from jsonschema import ValidationError, validate

projects_blueprint = Blueprint('projects', __name__)


@projects_blueprint.route('/api/projects', methods=["GET"])
@jwt_required()
def getProjects():
    user_projects = db.projects.find({"user": get_current_user()['_id']}, {"user": 0})
    return jsonify({"projects": list(user_projects)})


@projects_blueprint.route('/api/create-projects', methods=["POST"])
@jwt_required()
def createProjects():
    data = request.json
    name = data.get("name")
    user_id = get_current_user()["_id"]
    description = data.get('description')
    name = create_slug(name)

    try:
        validate(data, projects_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    if db.projects.find_one({"name": name, "user":user_id}) == None:

        db.projects.insert_one({
            "_id":create_id(),
            "name": name,
            "description": description,
            "user": user_id,
            "created_at": datetime.now()
        })
        return jsonify({"success": "project created successfully"})
    else:
        return jsonify({"errors": "You already have a project of the same name"}), 400


@projects_blueprint.route('/api/delete-projects',methods=["DELETE"])
@jwt_required()
def deleteProjects():
    data = request.json
    name = data.get("name")
    user_id = get_current_user()['_id']

    if db.projects.find_one({"name" : name, "user":user_id}) == None:
        return jsonify({"errors" : "No such project exists in your project directory"})
    else:
        db.projects.delete_one({"name" :name, "user":user_id})
        return jsonify({"success" : "project succesfully removed"})




