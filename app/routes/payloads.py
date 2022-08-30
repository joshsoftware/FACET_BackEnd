from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id,get_current_user
from app.helpers.utils import has_access_to_project
from app.models.PayloadModel import PayloadModel, PayloadSchema

payloads_blueprint = Blueprint('payloads', __name__)
payload_schema = PayloadSchema()


@payloads_blueprint.route('/', methods=['GET'])
@payloads_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def get_payloads(id=0):
    try:
        user = get_current_user()
        project_id = get_project_id(request.args.get("project"))
        if has_access_to_project(project_id,user.id):
            if id!=0:
                data = PayloadModel.get_one_payload(id)
                return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

            data = PayloadModel.get_all_payloads(project_id)
            return jsonify({"payloads": data}), 200, {"content-type": "application/json; charset=UTF-8"}
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to access the project components"}),401
    except Exception as e:
        return jsonify(e), 400

@payloads_blueprint.route('/new', methods = ['POST'])
@jwt_required()
def create_payloads():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get('name'))
    req_data['project'] = get_project_id(req_data.get('project'))
    user = get_current_user()
    req_data['created_by'] = user.id
    req_data['modified_by'] = user.id
    if has_access_to_project(req_data['project'],user.id):
        try:
            data = payload_schema.load(req_data)
        except ValidationError as err:
            return jsonify(err), 400

        is_exist = PayloadModel.is_exist(data.get('name'), data.get('project'))

        if is_exist:
            return jsonify({"error": "You already have a payload of the same name in this project."}), 400

        payload = PayloadModel(data)
        payload.save()
        return jsonify({"success": "Payload created Successfully!!"}), 201
    else:
        return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"}),401

@payloads_blueprint.route('/delete/',methods=["DELETE"])
@jwt_required()
def delete_payload():
    req_data = request.json
    user = get_current_user()
    try:
        payload = PayloadModel.query.get(req_data.get('payload'))
    except Exception as e:
        return jsonify(str(e)),400
    if payload:
        if has_access_to_project(payload.project,user.id):
            payload.delete()
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}),401
    else:
        return jsonify({"error" : "No such payload exists"}),404
    return jsonify({"Success" : "payload deleted successfully"}),200

@payloads_blueprint.route('/update',methods=["PUT"])
@jwt_required()
def update_payload():
    req_data = request.json
    user = get_current_user()
    try:
        payload = req_data.get('id')
        payload = PayloadModel.query.get(payload)
        if payload:
            if has_access_to_project(payload.project,user.id): 
                if req_data.get('name'):
                    name = req_data.get('name')
                    payload.name = name
            
                if req_data.get('payload'):
                    new_payload = req_data.get('payload')
                    payload.payload = new_payload
            
                if req_data.get('expected_outcome'):
                    expected_outcome = req_data.get('expected_outcome')
                    payload.expected_outcome = expected_outcome
                
                if req_data.get('parameters'):
                    parameters = req_data.get('parameters')
                    payload.parameters = parameters
                    
                payload.update({'modified_by' : user.id})
            else:
                return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"}),401
        else:
            return jsonify({"Error" : "No such Payload exists"}),404
    except Exception as err:
        return jsonify(str(err)),400
    return jsonify({"Success" : "Payload updated successfully"}),200