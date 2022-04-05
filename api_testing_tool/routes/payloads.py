from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_current_user, jwt_required
from api_testing_tool import db
from api_testing_tool.helpers.utils import create_id

payloads_blueprint = Blueprint('payloads', __name__)


@payloads_blueprint.route('/api/create-payload', methods = ['POST'])
@jwt_required()
def create_payloads():
    data = request.json

    project_id = data.get("project_id")
    payload_name = data.get("name")
    # payload = data.get("payload")
    # expected_outcome = data.get("expected_outcome")

    if project_id=="" or payload_name=="":
        return jsonify({"errors":"All fields are Required!"})

    db.payloads.insert_one({
        "_id": create_id(),
        **data
    })

    return jsonify({"msg": "Payload created Successfully!!"})

        