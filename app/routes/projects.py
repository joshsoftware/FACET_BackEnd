from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from app.helpers import create_slug
from marshmallow import ValidationError
from app.models.ProjectModel import ProjectModel, ProjectSchema

projects_blueprint = Blueprint('projects', __name__)
project_schema = ProjectSchema()


@projects_blueprint.route('/', methods=["GET"])
@jwt_required()
def getProjects():
    print(get_current_user().id)
    projects = ProjectModel.get_all_projects(get_current_user().id)
    return jsonify({"projects": list(projects)})

@projects_blueprint.route('/new', methods=["POST"])
@jwt_required()
def createProjects():
    req_data = request.json
    req_data['user'] = get_current_user().id
    req_data['name'] = create_slug(req_data.get('name'))

    try:
        data = project_schema.load(req_data)
    except ValidationError as err:
        return jsonify(err), 400

    project_exist = ProjectModel.is_project_exist(data.get('name'), data.get('user'))

    if project_exist:
        return jsonify({"error": "You already have a project of the same name"}), 400

    project = ProjectModel(data)
    project.save()
    return jsonify({"success": "project created successfully"})
    

# @projects_blueprint.route('/api/delete-projects',methods=["DELETE"])
# @jwt_required()
# def deleteProjects():
#     data = request.json
#     name = data.get("name")
#     user_id = get_current_user()['_id']

#     if db.projects.find_one({"name" : name, "user":user_id}) == None:
#         return jsonify({"errors" : "No such project exists in your project directory"})
#     else:
#         db.projects.delete_one({"name" :name, "user":user_id})
#         return jsonify({"success" : "project succesfully removed"})




