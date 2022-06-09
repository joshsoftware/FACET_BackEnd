from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from app.models.UserModel import UserModel
from marshmallow import ValidationError
from app.helpers.utils import create_slug,get_current_user
from app.models.OrganizationModel import OrganizationModel,OrganizationSchema

organization_blueprint = Blueprint('organization',__name__)
organization_schema = OrganizationSchema()

@organization_blueprint.route('/new',methods = ["POST"])
@jwt_required()
def createOrganization():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get("name"))
    admin = get_current_user()
    req_data['created_by'] = admin.id
    try:
        data = organization_schema.load(req_data)
    except ValidationError as err:
        return jsonify(str(err)), 400
    
    organization_exist = OrganizationModel.does_organization_exist(data.get('name'))

    if organization_exist:
        return jsonify({"error": "There already exists an organization of the same name"}), 400
    
    organization = OrganizationModel(data)
    organization.admin.append(admin)
    organization.members.append(admin)
    organization.save()
    return jsonify({"success": "Organization created successfully \n All the best for your new venture!!!!"})

@organization_blueprint.route('/add',methods = ["POST"])
@jwt_required()
def add_members():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get("name"))
    admin = get_current_user().id
    organization = OrganizationModel.does_organization_exist(req_data['name'])
    try:
        if organization:
            for adminstrator in organization.admin:
                if adminstrator.id == admin:
                    if req_data.get('admin'):
                       admins = req_data['admin']
                       del req_data['admin']
                       for adm in admins:
                           id = UserModel.get_one_user(adm)
                           organization.admin.append(id)
                           organization.members.append(id)
                    if req_data.get('members'):
                        members = req_data['members']
                        del req_data['members']
                        for member in members:
                            id = UserModel.get_one_user(member)
                            organization.members.append(id)
                    organization.update()
                    return jsonify({"Success" : "New members added successfully"})
                
            return jsonify({"error" : "You do not have access to add members"})
    except Exception as e:
        return jsonify(str(e))
    return jsonify({"error" : "No  such organization exists!!!!"})
        