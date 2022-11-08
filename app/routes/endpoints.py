from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.helpers import create_slug, get_project_id, get_current_user
from marshmallow import ValidationError
from app.helpers.utils import has_access_to_project
from app.models.EndpointModel import EndpointModel, EndpointSchema

endpoints_blueprint = Blueprint('endpoints', __name__)
endpoint_schema = EndpointSchema()


@endpoints_blueprint.route('/', methods=["GET"])
@endpoints_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getEndpoints(id=0):
    try:
        user = get_current_user()
        project_id = get_project_id(request.args.get("project"))
        if not has_access_to_project(project_id, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401
        if id != 0:
            data = EndpointModel.get_one_endpoint(id)
            return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

        data = EndpointModel.get_all_endpoints(project_id)
        return jsonify({"endpoints": data}), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@endpoints_blueprint.route('/new', methods=["POST"])
@jwt_required()
def createEndpoints():
    try:
        req_data = request.json
        req_data['name'] = create_slug(req_data.get('name'))
        req_data['project'] = get_project_id(req_data.get('project'))
        user = get_current_user()
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        if not has_access_to_project(req_data['project'], user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401
        try:
            data = endpoint_schema.load(req_data)
        except ValidationError as err:
            return jsonify({"error": str(err)}), 400

        is_exist = EndpointModel.is_exist(data.get('name'), data.get('project'))

        if is_exist:
            return jsonify({"error": "You already have a endpoint of the same name in this project."}), 400

        endpoint = EndpointModel(data)
        endpoint.save()
        return jsonify({"message": "Endpoint created successfully!"}), 201
    except Exception as err:
        print(str(err))
        return jsonify({"error":"something went wrong"}),400


@endpoints_blueprint.route('/delete/', methods=["DELETE"])
@jwt_required()
def delete_endpoint():
    try:
        req_data = request.json
        user = get_current_user()
        try:
            endpoint = EndpointModel.query.get(req_data.get('endpoint'))
        except Exception as err:
            print(str(err))
            return jsonify({"error": "something went wrong"}), 400

        if not endpoint:
            return jsonify({"error": "No such endpoint exists"}), 404

        if not has_access_to_project(endpoint.project, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        endpoint.delete()
        return jsonify({"message": "Endpoint deleted successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error":"something went wrong"}),400

@endpoints_blueprint.route('/update', methods=["PUT"])
@jwt_required()
def update_endpoint():
    try:
        req_data = request.json
        user = get_current_user()
        endpoint = req_data.get('id')
        endpoint = EndpointModel.query.get(endpoint)
        if not endpoint:
            return jsonify({"error": "no such endpoint exists"}), 404

        if not has_access_to_project(endpoint.project, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        endpoint.name = req_data.get('name') if req_data.get('name') else endpoint.name

        endpoint.endpoint = req_data.get('endpoint') if req_data.get('endpoint') else endpoint.endpoint

        endpoint.update({'modified_by': user.id})
        return jsonify({"message": "Endpoint updated successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error":"something went wrong"})
