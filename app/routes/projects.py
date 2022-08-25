from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from app.helpers.utils import get_project_id, is_user_admin
from app.models.UserModel import UserModel
from app.helpers import create_slug
from marshmallow import ValidationError
from app.models.ProjectModel import ProjectModel, ProjectSchema

projects_blueprint = Blueprint('projects', __name__)
project_schema = ProjectSchema()


@projects_blueprint.route('/', methods=["GET"])
@jwt_required()
def getProjects():
    data = ProjectModel.get_all_projects(get_current_user().id)
    return jsonify({"projects": data}),200

@projects_blueprint.route('/members', methods=["GET"])
@jwt_required()
def getMembers():
    project = request.args.get('project')
    data = ProjectModel.get_one_project(get_project_id(project))
    project_admin_id = data['project_admin']
    data = data['project_members']
    
    # add field is_project_admin if user is project admin in the data
    data = [{**mem, 'is_project_admin':True} if mem['id']==project_admin_id else mem for mem in data]
    
    return jsonify({"project": project, "members": data, "project_admin": project_admin_id }),200

@projects_blueprint.route('/new', methods=["POST"])
@jwt_required()
def createProjects():
    req_data = request.json
    user = get_current_user()
    if is_user_admin(user.id):
        req_data['project_admin'] = user.id
        req_data['name'] = create_slug(req_data.get('name'))
        
        try:
            data = project_schema.load(req_data)
        except ValidationError as err:
            return jsonify(err), 400

        project_exist = ProjectModel.is_project_exist(data.get('name'), data.get('project_admin'))

        if project_exist:
            return jsonify({"error": "You already have a project of the same name"}), 400

        super_admin = UserModel.query.filter_by(is_super_admin=True).first()
        project = ProjectModel(data)
        project.project_members.append(user)
        project.project_members.append(super_admin)
        project.save()
        return jsonify({"success": "project created successfully"}),200
    else:
        return jsonify({"Error" : "You do not possess the admin rights to create a project, kindly contact the super admin for recieving admin privileges"}),401


@projects_blueprint.route('/delete',methods=["DELETE"])
@jwt_required()
def delete_project():
    req_data = request.json
    user = get_current_user()
    try:
        project = ProjectModel.query.get(req_data.get('project'))
    except Exception as e:
        return jsonify(str(e)),400
    if project:
        if user.id == project.project_admin:
            project.delete()
        else:
            return jsonify({"error" : "You do not possess the admin rights to delete the project"}),401
    else:
        return jsonify({"error" : "No such project exists"}),404
    return jsonify({"Success" : "project deleted successfully"}),200

@projects_blueprint.route('/members/add',methods=["POST"])
@jwt_required()
def add_members():
    req_data = request.json
    req_data['project'] = create_slug(req_data.get('project'))
    admin = get_current_user().id
    project = ProjectModel.is_project_exist(req_data['project'], admin)
    try:
        if project:
            if admin == project.project_admin:
                members = req_data['members']
                del req_data['members']
                for member in members:
                    id = UserModel.get_one_user(member)
                    project.project_members.append(id)
                project.update({'modified_by': admin})
                return jsonify({"Success" : "New members added successfully"}),200
            else:
                return jsonify({"error" : "You do not have the admin rights to add members"}),401
    except Exception as e:
        return jsonify(str(e)),400
    return jsonify({"error" : "No such project exists!!!!"}),404

@projects_blueprint.route('/members/remove',methods=["POST"])
@jwt_required()
def remove_members():
    req_data = request.json
    req_data['project'] = create_slug(req_data['project'])
    admin = get_current_user().id
    project = ProjectModel.is_project_exist(req_data['project'],admin)
    try:
        if project:
            if admin == project.project_admin:
                members = req_data['members']
                del req_data['members']
                for member in members:
                    id = UserModel.get_one_user(member)
                    project.project_members.remove(id)
                project.update({'modified_by':admin})
                return jsonify({"Success":"Members removed successfully"}),200
            else:
                return jsonify({"Error": "You do not have the admin rights to delete members"}),401
    except Exception as e:
        return jsonify(str(e)),400
    return jsonify({"Error" : "No such project exists"}),404