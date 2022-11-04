from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from jsonschema import ValidationError
from app.helpers import create_slug, get_project_id, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.HeaderModel import HeaderModel, HeaderSchema

headers_blueprint = Blueprint('headers', __name__)
header_schema = HeaderSchema()


@headers_blueprint.route('/', methods=["GET"])
@headers_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getHeaders(id=0):
    try:
        user = get_current_user()
        project_id = get_project_id(request.args.get("project"))
        if not has_access_to_project(project_id, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id == 0:
            data = HeaderModel.get_all_headers(project_id)
            return jsonify({"headers": data}), 200, {"content-type": "application/json; charset=UTF-8"}

        data = HeaderModel.get_one_header(id)
        return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@headers_blueprint.route('/new', methods=["POST"])
@jwt_required()
def createHeaders():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get('name'))
    req_data['project'] = get_project_id(req_data.get('project'))
    user = get_current_user()
    req_data['created_by'] = user.id
    req_data['modified_by'] = user.id
    if not has_access_to_project(req_data['project'], user.id):
        return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401
    
    try:
        data = header_schema.load(req_data)
    except ValidationError as err:
        return jsonify(err), 400

    is_exist = HeaderModel.is_exist(data.get('name'), data.get('project'))

    if is_exist:
        return jsonify({"error": "You already have a header of the same name in this project."}), 400

    endpoint = HeaderModel(data)
    endpoint.save()
    return jsonify({"message": "Header created successfully!"}), 201


@headers_blueprint.route('/delete/', methods=["DELETE"])
@jwt_required()
def delete_header():
    req_data = request.json
    user = get_current_user()
    try:
        header = HeaderModel.query.get(req_data.get('header'))
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400
    
    if not header:
        return jsonify({"error": "No such header exists"}), 404
    
    if not has_access_to_project(header.project, user.id):
        return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401
    
    header.delete()
    return jsonify({"message": "Header deleted successfully"}), 200


@headers_blueprint.route('/update', methods=["PUT"])
@jwt_required()
def update_header():
    req_data = request.json
    user = get_current_user()
    try:
        header = req_data.get('id')
        header = HeaderModel.query.get(header)
        if not header:
            return jsonify({"error": "No such header exists"}), 404
        
        if not has_access_to_project(header.project, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401
        
        if req_data.get('name'):
            name = req_data.get('name')
            header.name = name
        
        if req_data.get('header'):
            new_header = req_data.get('header')
            header.header = new_header
        
        header.update({'modified_by': user.id})
        return jsonify({"message": "Header updated successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400
