from signal import pause
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.ExpectedOutcomeModel import ExpectedOutcomeModel, ExpectedOutcomeSchema
from app.models.PayloadModel import PayloadModel, PayloadSchema

payloads_blueprint = Blueprint('payloads', __name__)
payload_schema = PayloadSchema()


@payloads_blueprint.route('/', methods=['GET'])
@payloads_blueprint.route('/<string:id>', methods=['GET'])
@jwt_required()
def get_payloads(id=0):
    try:
        user = get_current_user()
        project_id = get_project_id(request.args.get("project"))
        if not has_access_to_project(project_id, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id != 0:
            data = PayloadModel.get_one_payload(id)
            return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

        data = PayloadModel.get_all_payloads(project_id)
        return jsonify({"payloads": data}), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@payloads_blueprint.route('/new', methods=['POST'])
@jwt_required()
def create_payloads():
    try:
        req_data = request.json
        req_data['name'] = create_slug(req_data.get('name'))
        req_data['project'] = get_project_id(req_data.get('project'))
        user = get_current_user()
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        expected_outcome = req_data['expected_outcome']
        del req_data['expected_outcome']
        if not (type(expected_outcome) is list and len(expected_outcome) > 0):
            return jsonify({"error": "You cannot insert an empty expected outcome"}), 400
        if not has_access_to_project(req_data['project'], user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        try:
            data = payload_schema.load(req_data)
        except ValidationError as err:
            return jsonify({"error": str(err)}), 400

        is_exist = PayloadModel.is_exist(data.get('name'), data.get('project'))
        if is_exist:
            return jsonify({"error": "You already have a payload of the same name in this project."}), 400

        payload = PayloadModel(data)
        payload.save()
        try:
            for exp_outcome in expected_outcome:
                if not (exp_outcome['expected_outcome'] is not None and is_expected_outcome_valid(exp_outcome['expected_outcome'])):
                    raise Exception(
                        'You cannot pass empty expected outcome in the payload')
                exp_outcome['payload'] = payload.id
                exp_outcome['created_by'] = user.id
                exp_outcome['modified_by'] = user.id
                data = ExpectedOutcomeSchema().load(exp_outcome)
                exp_outcome = ExpectedOutcomeModel(data)
                exp_outcome.save()
        except Exception as err:
            payload.delete()
            print(str(err))
            return jsonify({"error": "something went wrong"}), 400

        return jsonify({"message": "Payload created Successfully!!"}), 201
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"})


@payloads_blueprint.route('/delete/', methods=["DELETE"])
@jwt_required()
def delete_payload():
    try:
        req_data = request.json
        user = get_current_user()
        try:
            payload = PayloadModel.query.get(req_data.get('payload'))
        except Exception as err:
            print(err)
            return jsonify({"error": "something went wrong"}), 400

        if not payload:
            return jsonify({"error": "No such payload exists"}), 404

        if not has_access_to_project(payload.project, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401

        payload.delete()
        return jsonify({"message": "payload deleted successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error":"something went wrong"}),400


@payloads_blueprint.route('/update', methods=["PUT"])
@jwt_required()
def update_payload():
    try:
        req_data = request.json
        user = get_current_user()
        payload = req_data.get('id')
        payload = PayloadModel.query.get(payload)
        if not payload:
            return jsonify({"error": "No such Payload exists"}), 404

        if not has_access_to_project(payload.project, user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        payload.name = req_data.get('name') if req_data.get('name') else payload.name

        payload.payload = req_data.get('payload') if req_data.get('payload') else payload.payload

        if req_data.get('expected_outcome'):
            expected_outcome = req_data.get('expected_outcome')
            for exp_outcome in expected_outcome:
                is_exist = ExpectedOutcomeModel.is_exist(
                    name=exp_outcome['name'], payload_id=payload.id)
                if is_exist:
                    updated_exp_outcome = ExpectedOutcomeModel.query.get(
                        exp_outcome['id'])
                    updated_exp_outcome.name = exp_outcome['name']
                    updated_exp_outcome.expected_outcome = exp_outcome['expected_outcome']
                    updated_exp_outcome.update({'modified_by': user.id})
                else:
                    exp_outcome['payload'] = payload.id
                    exp_outcome['created_by'] = user.id
                    exp_outcome['modified_by'] = user.id
                    try:
                        data = ExpectedOutcomeSchema().dump(exp_outcome)
                        new_exp_outcome = ExpectedOutcomeModel(data)
                        new_exp_outcome.save()
                    except Exception as err:
                        print(err)
                        return jsonify({"error": "something went wrong"}), 400

        payload.parameters = req_data.get('parameters') if req_data.get('parameters') else payload.parameters

        payload.update({'modified_by': user.id})
        return jsonify({"message": "Payload updated successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


def is_expected_outcome_valid(expected_outcome):
    outcome = False
    if type(expected_outcome) is list and len(expected_outcome) > 0:
        if type(expected_outcome[0]) is dict and len(expected_outcome[0]) > 0:
            outcome = True
    return outcome
