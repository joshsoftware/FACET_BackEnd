from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id
from app.models.PayloadModel import PayloadModel, PayloadSchema

payloads_blueprint = Blueprint('payloads', __name__)
payload_schema = PayloadSchema()


@payloads_blueprint.route('/', methods=['GET'])
@payloads_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def get_payloads(id=0):
    try:
        project_id = get_project_id(request.args.get("project"))
        if id!=0:
            data = PayloadModel.get_one_payload(id)
            return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

        data = PayloadModel.get_all_payloads(project_id)
        return jsonify({"payloads": data}), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as e:
        return jsonify(e), 400

@payloads_blueprint.route('/new', methods = ['POST'])
@jwt_required()
def create_payloads():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get('name'))
    req_data['project'] = get_project_id(req_data.get('project'))

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

