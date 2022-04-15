from flask import Blueprint,jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool import db
from api_testing_tool.helpers import create_id, validation_error, create_slug, get_project_id
from jsonschema import ValidationError, validate
from api_testing_tool.schema import endpoints_schema

endpoints_blueprint = Blueprint('endpoints', __name__)

@endpoints_blueprint.route('/api/endpoints',methods = ["GET"])
@jwt_required()
def getEndpoints():  
    try:
        project_id = get_project_id(request.args.get("project"))
        project_endpoints = db.endpoints.find({"project_id" : project_id, "user":get_current_user()['_id']})
        return jsonify({"endpoints": list(project_endpoints)}), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as e :
        return jsonify(e), 400

@endpoints_blueprint.route('/api/create-endpoints',methods=["POST"])
@jwt_required()
def createEndpoints():
    data = request.json
    endpoint = data.get("endpoint")
    name = create_slug(data.get("name"))
    project_name = data.get("project_name")
    user_id = get_current_user()['_id']
    project_id = db.projects.find_one({"name": project_name, "user":user_id})["_id"]

    try:
        validate(data, endpoints_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    if project_id != None:
        db.endpoints.insert_one({
            "_id" : create_id(),
            "endpoint" : endpoint,
            "name" : name,
            "project_id" : project_id,
            "user": get_current_user()["_id"]
        })
        return jsonify({"success": "endpoint added successfully"})
    else:
        return jsonify({"error" : "invalid project details"})

# @endpoints_blueprint.route('api/update-endpoints',method = ["POST"])
# @jwt_required()
# def updateEndpoints():
#     data = request.json
#     endpoint_id = data.get("endpoint_id")
    