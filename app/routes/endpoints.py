from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from app.helpers import create_slug, get_project_id
from marshmallow import ValidationError
from app.models.EndpointModel import EndpointModel, EndpointSchema

endpoints_blueprint = Blueprint('endpoints', __name__)
endpoint_schema = EndpointSchema()

@endpoints_blueprint.route('/',methods = ["GET"])
@endpoints_blueprint.route('/<string:id>',methods = ["GET"])
@jwt_required()
def getEndpoints(id=0):  
    try:
        project_id = get_project_id(request.args.get("project"))
        if id!=0:
            endpoint = EndpointModel.get_one_endpoint(id)
            data = endpoint_schema.dump(endpoint)
            return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

        endpoints = EndpointModel.get_all_endpoints(project_id)
        data = endpoint_schema.dump(endpoints, many=True)
        return jsonify({"endpoints": data}), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as e :
        return jsonify(e), 400

@endpoints_blueprint.route('/new',methods=["POST"])
@jwt_required()
def createEndpoints():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get('name'))
    req_data['project'] = get_project_id(req_data.get('project'))

    try:
        data = endpoint_schema.load(req_data)
    except ValidationError as err:
        return jsonify(err), 400

    is_exist = EndpointModel.is_exist(data.get('name'), data.get('project'))

    if is_exist:
        return jsonify({"error": "You already have a endpoint of the same name in this project."}), 400

    endpoint = EndpointModel(data)
    endpoint.save()
    return jsonify({"success": "Endpoint created successfully!"}), 201
    
