from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool import db
from api_testing_tool.helpers import create_slug, create_id

projects_blueprint = Blueprint('projects', __name__)


@projects_blueprint.route('/api/projects', methods=["GET"])
@jwt_required()
def getProjects():
    user_projects = db.projects.find({"user": get_current_user()['_id']})
    return jsonify({"projects": list(user_projects)})


@projects_blueprint.route('/api/create-projects', methods=["POST"])
@jwt_required()
def createProjects():
    data = request.json
    project_name = data.get("name")
    user_id = get_current_user()["_id"]
    slug = create_slug(project_name)

    if db.projects.find_one({"slug": slug, "user":user_id}) == None:

        if len(project_name) < 3:
            return jsonify({"errors": "Project length should be of minimum 3 letters"})

        db.projects.insert_one({
            "_id":create_id(),
            "name": project_name, 
            "user": user_id, 
            "slug" : slug
        })
        return jsonify({"success": "project created successfully"})
    else:
        return jsonify({"errors": "You already have a project of the same name"})


@projects_blueprint.route('/api/delete-projects',methods=["DELETE"])
@jwt_required()
def deleteProjects():
    data = request.json
    slug = data.get("slug")
    user_id = get_current_user()['_id']

    if db.projects.find_one({"slug" : slug, "user":user_id}) == None:
        return jsonify({"errors" : "No such project exists in your project directory"})
    else:
        db.projects.delete_one({"slug" :slug, "user":user_id})
        return jsonify({"success" : "project succesfully removed"})




