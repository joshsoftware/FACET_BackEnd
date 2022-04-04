from flask import Blueprint,jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool import db
from api_testing_tool.helpers.utils import create_id

endpoints_blueprint = Blueprint('endpoints', __name__)

@endpoints_blueprint.route('/api/endpoints',methods = ["GET"])
@jwt_required()
def getEndpoints():
    data = request.json
    project_id = data.get("project_id")
    project_endpoints = db.endpoints.find({"project_id" : project_id})
    return jsonify({"endpoints": list(project_endpoints)})

@endpoints_blueprint.route('/api/create-endpoints',methods=["POST"])
@jwt_required()
def createEndpoints():
    data = request.json
    endpoint = data.get("endpoint")
    name = data.get("name")
    project_name_slug = data.get("project_name_slug")
    user_id = get_current_user()['_id']
    project_id = db.projects.find_one({"slug": project_name_slug, "user":user_id})["_id"]
    if project_id != None:
        db.endpoints.insert_one({
            "_id" : create_id(),
            "endpoint" : endpoint,
            "name" : name,
            "project_id" : project_id
        })
        return jsonify({"success": "endpoint added successfully"})
    else:
        return jsonify({"error" : "invalid project details"})

# @endpoints_blueprint.route('api/update-endpoints',method = ["POST"])
# @jwt_required()
# def updateEndpoints():
#     data = request.json
#     endpoint_id = data.get("endpoint_id")
    