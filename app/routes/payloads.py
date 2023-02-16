"""
Payloads API module for
performing CRUD operations on
 -Payload Model
 -Expected Outcome model

There exists a combined single API
routes for performing CRUD operations
on both payloadmodel and expected outcome
model
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.ExpectedOutcomeModel import ExpectedOutcomeModel, ExpectedOutcomeSchema
from app.models.PayloadModel import PayloadModel, PayloadSchema

payloads_blueprint = Blueprint("payloads", __name__)
payload_schema = PayloadSchema()


@payloads_blueprint.route("/", methods=["GET"])
@payloads_blueprint.route("/<string:payload_id>", methods=["GET"])
@jwt_required()
def get_payloads(payload_id=0):
    """
    GET API route for fetching
    payload and its expected outcomes
    Requires:
        - method: GET
        - JWT Bearer token in Authorization header
        - Project name in params
        - payload id(optional for single record)
    Response:
        - Error message with status code 400 if anything goes wrong due to
            faulty json or unknown factors,
        - Error message with status code 401 if anybody without project access
            tries hit the API
        - If success, then json response with status code 200, where json look like :
            {"payloads": list of dicitonaries}
    """
    try:
        user = get_current_user()
        project_id = get_project_id(request.args.get("project"), user.user_organization)
        logging.info(
            "GET request to fetch payload by user:%s with params:%s and url:%s",
            user.id,
            dict(request.args),
            request.url,
        )
        if not has_access_to_project(project_id, user.id):
            logging.info("GET request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": "Unauthorised access,you do not have access to this project component"
                    }
                ),
                401,
            )

        if payload_id != 0:
            data = PayloadModel.get_one_payload(payload_id)
            logging.info(
                "GET request successful, payload returned successfully for payload id:%s",
                payload_id,
            )
            return jsonify(data), 200

        data = PayloadModel.get_all_payloads(project_id)
        logging.info(
            "GET request successful, payloads returned successfully for project id:%s",
            project_id,
        )
        return jsonify({"payloads": data}), 200
    except Exception as err:
        logging.exception("GET request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"}), 400


@payloads_blueprint.route("/new", methods=["POST"])
@jwt_required()
def create_payloads():
    """
    POST request route for creating a new payload with
        an array of expected outcomes and parameters
    Request requirements:
        - method : POST
        - JWT Bearer token in Authorization header
        - body data:
            {
                name: string,
                payload: dictionary,
                project: project_name,
                expected_outcome : array of dictionaries,
                parameters :dictionary
            }
    Response:
        - if successful, then a json message of success with status code 200
        - error message with status code 400, with the message
            'A payload/expected outcome of the same name already exists' if it already exists
        - error message with status code 400 and message 'something went wrong'
            if faulty input of any sort is provided
    """
    try:
        req_data = request.json
        user = get_current_user()
        req_data["name"] = create_slug(req_data.get("name"))
        req_data["project"] = get_project_id(
            req_data.get("project"), user.user_organization
        )
        logging.info(
            "POST request to create payload by user:%s with payload:%s",
            user.id,
            req_data,
        )
        req_data["created_by"] = user.id
        req_data["modified_by"] = user.id
        expected_outcome = req_data["expected_outcome"]
        del req_data["expected_outcome"]
        if not (isinstance(expected_outcome, list) and len(expected_outcome) > 0):
            logging.info("POST request failed as faulty expected outcome provided")
            return (
                jsonify({"error": "You cannot insert an empty expected outcome"}),
                400,
            )
        if not has_access_to_project(req_data["project"], user.id):
            logging.info("POST request failed due to unauthorised access")
            return (
                jsonify({"error": "You do not have access to this project components"}),
                401,
            )

        try:
            data = payload_schema.load(req_data)
        except ValidationError as err:
            logging.error("payload creation failed due to the following error %s", err)
            return jsonify({"error": str(err)}), 400

        is_exist = PayloadModel.is_exist(data.get("name"), data.get("project"))
        if is_exist:
            logging.info("payload creation failed due to duplicate entry")
            return (
                jsonify(
                    {
                        "error": "You already have a payload of the same name in this project."
                    }
                ),
                400,
            )

        payload = PayloadModel(data)
        payload.save()
        try:
            for exp_outcome in expected_outcome:
                if not (
                    exp_outcome["expected_outcome"] is not None
                    and is_expected_outcome_valid(exp_outcome["expected_outcome"])
                ):
                    logging.info(
                        "POST request to create payload failed as \
                        empty expected outcome was provided in the payload"
                    )
                    return (
                        jsonify(
                            {
                                "error": "You cannot pass empty expected outcome in the payload"
                            }
                        ),
                        400,
                    )
                # expected outcome validations for duplicate entry
                exp_outcome["payload"] = payload.id
                exp_outcome["created_by"] = user.id
                exp_outcome["modified_by"] = user.id
                data = ExpectedOutcomeSchema().load(exp_outcome)
                data["name"] = create_slug(data["name"])
                if ExpectedOutcomeModel.is_exist(
                    name=data["name"], payload_id=payload.id
                ):
                    logging.info(
                        "Payload creation failed as duplicate expected outcomes"
                    )
                    raise Exception(
                        f"Duplicate entry provided for expected outcome:{data['name']}"
                    )
                exp_outcome = ExpectedOutcomeModel(data)
                exp_outcome.save()
        except Exception as err:
            payload.delete()
            logging.exception(
                "POST request to create payload failed due to the following error:%s",
                err,
            )
            return jsonify({"error": str(err)}), 400
        logging.info("payload created successfully with its expected outcomes")
        return jsonify({"message": "Payload created Successfully!!"}), 201
    except Exception as err:
        logging.exception("POST request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"})


@payloads_blueprint.route("/delete/", methods=["DELETE"])
@jwt_required()
def delete_payload():
    """
    DELETE route to delete an organization
    Request Requiers:
    - method: DELETE
    - JWT Bearer token in Authorization header
    - body data:
        {
            payload : payload_id
        }
    Response:
        - success message with status code 200 if everything is successful
        - error message with status code 400 and
            message "faulty input" if faulty inputs are provided
        - error message with status code 404
            and message "organization not found" if the organization does not exist
        - error message with status code 401 if somebody without access to the project hits the api
    """
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(
            "DELETE request to delete payload by user:%s with payload:%s",
            user.id,
            req_data,
        )
        try:
            payload = PayloadModel.query.get(req_data.get("payload"))
        except Exception as err:
            logging.exception(
                "DELETE request failed due to the following error:%s", err
            )
            return jsonify({"error": "something went wrong"}), 400

        if not payload:
            logging.info(
                "DELETE request failed as no such payload exists for the project"
            )
            return jsonify({"error": "No such payload exists"}), 404

        if not has_access_to_project(payload.project, user.id):
            logging.info("DELETE request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": "Unauthorised access you do not have access to this project component"
                    }
                ),
                401,
            )

        payload.delete()
        logging.info("payload deleted sucessfully")
        return jsonify({"message": "payload deleted successfully"}), 200
    except Exception as err:
        logging.exception("DELETE request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"}), 400


@payloads_blueprint.route("/update", methods=["PUT"])
@jwt_required()
def update_payload():
    """
    PUT API to update an payload, expected outcome and parameters
    Reqest requires:
        - method: PUT
        - JWT Bearer token in Authorization header
        - body data:
            {
            }
    Response:
        - success message with status code 200 if everything is successful
        - error message with status code 400 and message "something went wrong"
            if anything goes wrong due to unknown reasons
        - error message with status code 404 with message "payload not found"
            if the payload does not exist
        - error message with status code 400 if an existing new name is provided
        - error message with status code 401
            if somebody without access to the payload hits the api
    """
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(
            "PUT request to update payload by user:%s with payload:%s",
            user.id,
            req_data,
        )
        payload = req_data.get("id")
        payload = PayloadModel.query.get(payload)
        if not payload:
            logging.info("PUT request failed as no such payload exists for the project")
            return jsonify({"error": "No such Payload exists"}), 404

        if not has_access_to_project(payload.project, user.id):
            logging.info("PUT request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": "Unauthorised access you do not have access to this project component"
                    }
                ),
                401,
            )

        payload.name = req_data.get("name") if req_data.get("name") else payload.name

        payload.payload = (
            req_data.get("payload") if isinstance(req_data, dict) else payload.payload
        )

        if req_data.get("expected_outcome"):
            expected_outcome = req_data.get("expected_outcome")
            for exp_outcome in expected_outcome:
                if exp_outcome.get("id"):
                    updated_exp_outcome = ExpectedOutcomeModel.query.get(
                        exp_outcome["id"]
                    )
                    updated_exp_outcome.name = exp_outcome["name"]
                    updated_exp_outcome.expected_outcome = exp_outcome[
                        "expected_outcome"
                    ]
                    updated_exp_outcome.update({"modified_by": user.id})
                else:
                    exp_outcome["payload"] = payload.id
                    exp_outcome["created_by"] = user.id
                    exp_outcome["modified_by"] = user.id
                    is_exist = ExpectedOutcomeModel.is_exist(
                        name=create_slug(exp_outcome["name"]), payload_id=payload.id
                    )
                    if is_exist:
                        logging.info(
                            "PUT request failed due to duplicate expected outcome"
                        )
                        return (
                            jsonify(
                                {
                                    "error": f"Duplicate entry provided for expected outcome:{exp_outcome['name']}"
                                }
                            ),
                            400,
                        )
                    try:
                        exp_outcome['name'] = create_slug(exp_outcome['name'])
                        data = ExpectedOutcomeSchema().dump(exp_outcome)
                        new_exp_outcome = ExpectedOutcomeModel(data)
                        new_exp_outcome.save()
                    except Exception as err:
                        logging.info(
                            "PUT request to update payload failed due to the following error:%s",
                            err,
                        )
                        return jsonify({"error": "something went wrong"}), 400

        payload.parameters = (
            req_data.get("parameters")
            if isinstance(req_data.get("parameters"), dict)
            else payload.parameters
        )

        payload.update({"modified_by": user.id})
        logging.info("payload updated sucessfully")
        return jsonify({"message": "Payload updated successfully"}), 200
    except Exception as err:
        logging.exception("PUT request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"}), 400


def is_expected_outcome_valid(expected_outcome):
    """
    function to check if the provided expected outcome
    is provided in proper format and is not null
    """
    outcome = False
    if isinstance(expected_outcome, list) and len(expected_outcome) > 0:
        if isinstance(expected_outcome[0], dict) and len(expected_outcome[0]) > 0:
            outcome = True
    return outcome
