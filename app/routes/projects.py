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
    project = request.args.get('project')
    if project:
        project = get_project_id(project)
    user = get_current_user().id
    if project:
        data = ProjectModel.get_one_project(project, user)
        if not data:
            return jsonify({"error": 'Project Not Found'}), 404
        data['is_project_admin'] = data['project_admin']==user
        return jsonify(data), 200
    data = ProjectModel.get_all_projects(get_current_user().id)
    return jsonify({"projects": data}),200

@projects_blueprint.route('/members', methods=["GET"])
@jwt_required()
def getMembers():
    project = request.args.get('project')
    user = get_current_user().id
    data = ProjectModel.get_one_project(get_project_id(project), user)
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

        project_exist = ProjectModel.is_project_exist(data.get('name'))

        if project_exist:
            return jsonify({"error": "A project of the same name already exists"}), 400

        super_admin = UserModel.query.filter_by(is_super_admin=True).first()
        project = ProjectModel(data)
        project.project_members.append(user)
        if user.id != super_admin.id:
            project.project_members.append(super_admin)
        project.save()
        return jsonify({"message": "project created successfully"}),200
    else:
        return jsonify({"error" : "You do not possess the admin rights to create a project, kindly contact the super admin for recieving admin privileges"}),401


@projects_blueprint.route('/update-name', methods=['POST'])
@jwt_required()
def updateName():
    req_data = request.json
    user = get_current_user().id
    project_name = req_data.get('project')
    new_project_name = req_data.get('newProjName')
    if project_name and new_project_name:
        project = ProjectModel.query.get(get_project_id(project_name))
        if project:
            if project_name!=new_project_name:
                if project.project_admin==user:
                    #backend stores data only in slug format, hence converting new name to slug for proper verification
                    new_project_name = create_slug(new_project_name)
                    if not ProjectModel.is_project_exist(new_project_name):
                        project.name = new_project_name
                        project.update()
                    else:
                        return jsonify({"error": "Project name already exist!"}), 400
                else:
                    return jsonify({"error": "You do not have access to update the project name"}), 401
            else:
                return jsonify({"error": "New project name must be different from previous name"}), 400
        else:
            return jsonify({"error": "Project not found with given name!"}), 404
    else:
        return jsonify({"error": "Something Went Wrong!"}), 400
    return jsonify({'message': "Project name updated successfully!"}), 200

@projects_blueprint.route('/delete/',methods=["DELETE"])
@jwt_required()
def delete_project():
    try:
        req_data = request.json
        user = get_current_user()
        project_id = get_project_id(req_data.get('project'))
        project = ProjectModel.query.get(project_id)
        if project:
            if user.id == project.project_admin:
                project.delete()
            else:
                return jsonify({"error" : "You do not possess the admin rights to delete the project"}),401, {"content-type": "application/json; charset=UTF-8"}
        else:
            return jsonify({"error" : "No such project exists"}),404, {"content-type": "application/json; charset=UTF-8"}
        return jsonify({"message" : "project deleted successfully"}),200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400, {"content-type": "application/json; charset=UTF-8"}

@projects_blueprint.route('/members/add',methods=["POST"])
@jwt_required()
def add_members():
    req_data = request.json
    req_data['project'] = create_slug(req_data.get('project'))
    admin = get_current_user().id
    project = ProjectModel.is_project_exist(req_data['project'])
    try:
        if project:
            if admin == project.project_admin:
                members = req_data['members']
                del req_data['members']
                for member in members:
                    id = UserModel.get_one_user(member)
                    project.project_members.append(id)
                project.update({'modified_by': admin})
                return jsonify({"message" : "New members added successfully"}),200
            else:
                return jsonify({"error" : "You do not have the admin rights to add members"}),401
    except Exception as err:
        print(str(err))
        return jsonify({"error":"something went wrong"}),400
    return jsonify({"error" : "No such project exists!!!!"}),404

@projects_blueprint.route('/members/remove',methods=["DELETE"])
@jwt_required()
def remove_members():
    req_data = request.json
    req_data['project'] = create_slug(req_data['project'])
    admin = get_current_user().id
    project = ProjectModel.is_project_exist(req_data['project'])
    try:
        if project:
            if admin == project.project_admin:
                members = req_data['members']
                del req_data['members']
                for member in members:
                    id = UserModel.get_one_user(member)
                    project.project_members.remove(id)
                project.update({'modified_by':admin})
                return jsonify({"message":"Members removed successfully"}),200
            else:
                return jsonify({"error": "You do not have the admin rights to delete members"}),401
    except Exception as err:
        print(str(err))
        return jsonify({"error":"something went wrong"}),400
    return jsonify({"error" : "No such project exists"}),404