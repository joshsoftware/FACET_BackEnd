from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from app.helpers.utils import get_project_id, is_user_admin
from app.models.UserModel import UserModel
from app.helpers import create_slug
from marshmallow import ValidationError
from app.models.ProjectModel import ProjectModel, ProjectSchema
import logging

projects_blueprint = Blueprint('projects', __name__)
project_schema = ProjectSchema()


@projects_blueprint.route('/', methods=["GET"])
@jwt_required()
def getProjects():
    try:
        project = request.args.get('project')
        user = get_current_user().id
        logging.info(f"GET request to fetch project by user:{user} with params:{dict(request.args)} and url:{request.url}")
        if project:
            project = get_project_id(project)
        if project:
            data = ProjectModel.get_one_project(project, user)
            if not data:
                return jsonify({"error": 'Project Not Found'}), 404
            data['is_project_admin'] = data['project_admin']==user
            logging.info(f"GET request successful, project returned successfully for project id:{id}")
            return jsonify(data), 200
        data = ProjectModel.get_all_projects(get_current_user().id)
        logging.info(f"GET request successful, projects returned successfully for user:{user}")
        return jsonify({"projects": data}),200
    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@projects_blueprint.route('/members', methods=["GET"])
@jwt_required()
def getMembers():
    try:
        project = request.args.get('project')
        user = get_current_user().id
        logging.info(f"GET request to fetch all members of the project:{project} by user:{user}")
        data = ProjectModel.get_one_project(get_project_id(project), user)
        project_admin_id = data['project_admin']
        data = data['project_members']
        
        # add field is_project_admin if user is project admin in the data
        data = [{**mem, 'is_project_admin':True} if mem['id']==project_admin_id else mem for mem in data]
        logging.info(f"GET request successful, all member list returned successfully for project:{project}")
        return jsonify({"project": project, "members": data, "project_admin": project_admin_id }),200
    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400

@projects_blueprint.route('/new', methods=["POST"])
@jwt_required()
def createProjects():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"POST request to create project by user:{user.id} with payload:{req_data}")
        if not is_user_admin(user.id):
            logging.info(f"POST request failed due to unauthorised access")
            return jsonify({"error" : "You do not possess the admin rights to create a project, kindly contact the super admin for recieving admin privileges"}),401
        req_data['project_admin'] = user.id
        req_data['name'] = create_slug(req_data.get('name'))
        
        try:
            data = project_schema.load(req_data)
        except ValidationError as err:
            logging.error(f"project creation failed due to the following error {err}")
            return jsonify({"error": str(err)}), 400

        project_exist = ProjectModel.is_project_exist(data.get('name'))

        if project_exist:
            logging.info(f"project creation failed due to duplicate entry")
            return jsonify({"error": "A project of the same name already exists"}), 400

        super_admin = UserModel.query.filter_by(is_super_admin=True).first()
        project = ProjectModel(data)
        project.project_members.append(user)
        if user.id != super_admin.id:
            project.project_members.append(super_admin)
        project.save()
        logging.info(f"project created successfully")
        return jsonify({"message": "project created successfully"}),200
    except Exception as err:
        logging.exception(f"POST request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@projects_blueprint.route('/update-name', methods=['POST'])
@jwt_required()
def updateName():
    try:
        req_data = request.json
        user = get_current_user().id
        logging.info(f"POST request to update project name by user:{user.id} with payload:{req_data}")
        project_name = req_data.get('project')
        new_project_name = req_data.get('newProjName')
        if not (project_name and new_project_name):
            return jsonify({"error": "Something Went Wrong!"}), 400
        
        project = ProjectModel.query.get(get_project_id(project_name))
        
        if not project:
            logging.info(f"POST request to update project name failed as project does not exist")
            return jsonify({"error": "Project not found with given name!"}), 404
        
        if not(project_name!=new_project_name):
            logging.info(f"POST request to update project name failed as same name is provided for change")
            return jsonify({"error": "New project name must be different from previous name"}), 400
        
        if not(project.project_admin==user):
            logging.info(f"POST request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to update the project name"}), 401
            #backend stores data only in slug format, hence converting new name to slug for proper verification
        
        new_project_name = create_slug(new_project_name)
        if ProjectModel.is_project_exist(new_project_name):
            logging.info(f"POST request failed to update project name as another project exists with the newly suggested name")
            return jsonify({"error": "Project name already exist!"}), 400
        
        project.name = new_project_name
        project.update()
        logging.info(f"project name updated successfully")
        return jsonify({'message': "Project name updated successfully!"}), 200
    except Exception as err:
        logging.exception(f"POST request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@projects_blueprint.route('/delete/',methods=["DELETE"])
@jwt_required()
def delete_project():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"DELETE request to delete project by user:{user.id} with payload:{req_data}")
        project_id = get_project_id(req_data.get('project'))
        project = ProjectModel.query.get(project_id)
        if not project:
            logging.info(f"DELETE request failed as no such project")
            return jsonify({"error" : "No such project exists"}),404
        
        if not(user.id == project.project_admin):
            logging.info(f"DELETE request failed due to unauthorised access")
            return jsonify({"error" : "You do not possess the admin rights to delete the project"}),401
        
        project.delete()
        logging.info(f"project deleted sucessfully")
        return jsonify({"message" : "project deleted successfully"}),200
    except Exception as err:
        logging.exception(f"DELETE request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400

@projects_blueprint.route('/members/add',methods=["POST"])
@jwt_required()
def add_members():
    try:
        req_data = request.json
        req_data['project'] = create_slug(req_data.get('project'))
        admin = get_current_user().id
        logging.info(f"POST request to add members to project by user:{admin} with payload:{req_data}")
        project = ProjectModel.is_project_exist(req_data['project'])
        
        if not project:
            logging.info(f"POST request failed as no such project exists")
            return jsonify({"error" : "No such project exists!!!!"}),404
        
        if not(admin == project.project_admin):
            logging.info(f"POST request failed due to unauthorized access")
            return jsonify({"error" : "You do not have the admin rights to add members"}),401
        
        members = req_data['members']
        del req_data['members']
        for member in members:
            id = UserModel.get_one_user(member)
            project.project_members.append(id)
        project.update({'modified_by': admin})
        logging.info(f"new members added successfully to the project")
        return jsonify({"message" : "New members added successfully"}),200
    except Exception as err:
        logging.exception(f"POST request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}),400

@projects_blueprint.route('/members/remove',methods=["DELETE"])
@jwt_required()
def remove_members():
    try:
        req_data = request.json
        req_data['project'] = create_slug(req_data['project'])
        admin = get_current_user().id
        logging.info(f"DELETE request to remove project members by user:{admin} with payload:{req_data}")
        project = ProjectModel.is_project_exist(req_data['project'])
        if not project:
            logging.info(f"DELETE request failed as no such project exists")
            return jsonify({"error" : "No such project exists"}),404
        
        if not(admin == project.project_admin):
            logging.info(f"DELETE request failed due to unauthorised access")
            return jsonify({"error": "You do not have the admin rights to delete members"}),401
        
        members = req_data['members']
        del req_data['members']
        for member in members:
            id = UserModel.get_one_user(member)
            project.project_members.remove(id)
        project.update({'modified_by':admin})
        logging.info(f"project members removed sucessfully")
        return jsonify({"message":"Members removed successfully"}),200
    except Exception as err:
        logging.exception(f"DELETE request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}),400