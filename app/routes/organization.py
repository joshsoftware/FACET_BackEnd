from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
import jwt
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
    
    organization_exist = OrganizationModel.is_organization_exist(data.get('name'))

    if organization_exist:
        return jsonify({"error": "There already exists an organization of the same name"}), 400
    
    organization = OrganizationModel(data)
    organization.admin.append(admin)
    organization.save()
    return jsonify({"success": "Organization created successfully \n All the best for your new venture!!!!"})


 