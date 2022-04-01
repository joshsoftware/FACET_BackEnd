from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool import db
from bson.json_util import dumps
from api_testing_tool.helpers import create_slug
import json

projects_blueprint = Blueprint('projects', __name__)


@projects_blueprint.route('/api/projects', methods=["GET"])
@jwt_required()
def getProjects():
    user_projects = dumps(db.projects.find({"user": get_current_user()}))
    return jsonify(json.loads(user_projects))


@projects_blueprint.route('/api/create-projects', methods=["POST"])
@jwt_required()
def createProjects():
    data = request.json
    project_name = data.get("name")
    user_id = get_current_user()
    slug = create_slug(project_name)
    if db.projects.find_one({"slug": slug}) == None:
        if len(project_name) < 3:
            return jsonify({"errors": "Project length should be of minimum 3 letters"})
        db.projects.insert_one({"name": project_name, "user": user_id, "slug" : slug})
        return jsonify({"success": "project created successfully"})
    else:
        return jsonify({"errors": "You already have a project of the same name"})
