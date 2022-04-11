import re
from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from jsonschema import ValidationError, validate
from api_testing_tool import db
from api_testing_tool.helpers.utils import create_id
from api_testing_tool.schema import header_schema

headers_blueprint = Blueprint('headers', __name__)

@headers_blueprint.route('/api/headers',methods = ["GET"])
@jwt_required()
def getHeaders():
    data = request.json
    project_id = data.get("project_id")
    project_headers = db.headers.find({"project_id" : project_id})
    return jsonify({"headers" : list(project_headers)})


@headers_blueprint.route('/api/create-headers',methods = ["POST"])
@jwt_required()
def createHeaders():
    data = request.json
    project_id = data.get("project_id")
    header = data.get("header")
    name = data.get("name")
    
    try:
        validate(data, header_schema)
    except ValidationError as e:
        if len(e.relative_path) > 0:
            error = re.sub("'(.)*'", e.relative_path[0], str(e.message))
            error = {e.relative_path[0] : str(error)}
        else:
            error = str(e.message)
        return jsonify(error), 400

    db.headers.insert_one({
        "_id" : create_id(),
        "project_id" : project_id,
        "header" : header,
        "name" : name
    })
    return jsonify({"success": "header added succesfully"})