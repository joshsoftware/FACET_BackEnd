from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from jsonschema import ValidationError
from app.helpers import create_slug, get_project_id
from app.models.HeaderModel import HeaderModel, HeaderSchema

headers_blueprint = Blueprint('headers', __name__)
header_schema = HeaderSchema()

@headers_blueprint.route('/',methods = ["GET"])
@headers_blueprint.route('/<string:id>',methods = ["GET"])
@jwt_required()
def getHeaders(id=0):
    try:
        project_id = get_project_id(request.args.get("project"))
        if id==0:
            data = HeaderModel.get_all_headers(project_id)
            return jsonify({"headers": data}), 200, {"content-type": "application/json; charset=UTF-8"}

        data = HeaderModel.get_one_header(id)
        return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as e :
        return jsonify(e), 400


@headers_blueprint.route('/new', methods=["POST"])
@jwt_required()
def createHeaders():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get('name'))
    req_data['project'] = get_project_id(req_data.get('project'))

    try:
        data = header_schema.load(req_data)
    except ValidationError as err:
        return jsonify(err), 400

    is_exist = HeaderModel.is_exist(data.get('name'), data.get('project'))
    
    if is_exist:
        return jsonify({"error": "You already have a header of the same name in this project."}), 400

    endpoint = HeaderModel(data)
    endpoint.save()
    return jsonify({"success": "Header created successfully!"}), 201
    