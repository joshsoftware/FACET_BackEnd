import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_current_user, jwt_required
from jsonschema import ValidationError, validate
from api_testing_tool import db
from api_testing_tool.helpers import create_id, validation_error, create_slug
from api_testing_tool.schema import payload_schema

payloads_blueprint = Blueprint('payloads', __name__)


@payloads_blueprint.route('/api/create-payload', methods = ['POST'])
@jwt_required()
def create_payloads():
    data = request.json

    project_id = data.get("project_id")
    name = create_slug(data.get("name"))
    # payload = data.get("payload")
    # expected_outcome = data.get("expected_outcome")

    try:
        validate(data, payload_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    db.payloads.insert_one({
        "_id": create_id(),
        **data
    })

    return jsonify({"msg": "Payload created Successfully!!"})

        