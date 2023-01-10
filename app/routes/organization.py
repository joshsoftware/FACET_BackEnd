"""
organization API module for
performing CRUD operations, adding and removing
both admins and members within an organization
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_current_user, jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug
from app.helpers.utils import has_access_to_organization
from app.models.organization_model import OrganizationModel, OrganizationSchema

organization_blueprint = Blueprint("organizations", __name__)
organization_schema = OrganizationSchema()


@organization_blueprint.route("/", methods=["GET"])
@organization_blueprint.route("/<string:id>", methods=["GET"])
@jwt_required()
def get_organization_data(org_id=None):
    """
    GET request route for fetching data of a single
    organization
    Request requirements:
        - method: GET
        - JWT Bearer token in Authorization header
        - Organization ID
    Response:
        - Error message with status code 400
            if anything goes wrong due to faulty json or other unknown factors,
        - Error message with status code 401
            if anybody without organization access tries hit the API
        - If success, then json response with status code 200, where json look like :
            {"organization": organization_dictionary}
    """
    try:
        user = get_current_user()
        if org_id is None:
            logging.info(
                "Invalid request to fetch organization data as org_id was not provided"
            )
            return jsonify({"error": "invalid request"}), 400
        # to check if any association exists between user and the requested organization
        if not has_access_to_organization(organization_id=org_id, user=user):
            logging.info("GET request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": "Unauthorised access,you do not \
                        possess access to this organization"
                    }
                ),
                401,
            )
        organization = OrganizationModel.get_one_organization(organization_id=org_id)
        logging.info(
            "GET request to fetch details for organization:%d successfull by user:%s",
            org_id,
            user.name,
        )
        return jsonify({"organization": organization}), 200
    except Exception as err:
        logging.exception("GET request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"}), 400


@organization_blueprint.route("/new", methods=["POST"])
@jwt_required()
def create_organization():
    """
    POST request route for creating a new organization
    Request requirements:
        - method : POST
        - JWT Bearer token in Authorization header
        - body data:
            {
                name: string,
                description: string,
                contact_email_id: valid email string
            }
    Response:
        - if successful, then a json message of success with status code 200
        - error message with status code 400, with the message
            'An organization of the same name already exists' if it already exists
        - error message with status code 400 and message 'something went wrong'
            if faulty input of any sort is provided
    """
    try:
        request_data = request.json()
        user = get_current_user().id
        logging.info(
            "POST request to create organization by user:%d with payload:%s",
            user,
            request.url,
        )
        request_data["org_super_admin"] = user
        request_data["name"] = create_slug(request_data["name"])
        # Validating if the request data is valid as per organization Schema
        try:
            request_data = organization_schema.load(request_data)
        except ValidationError as err:
            logging.error(
                "organization created failed due to the following error: %s", err
            )
            return jsonify({"error": str(err)}), 400

        organization_exists = OrganizationModel.does_organization_exist(
            organization_name=request_data["name"]
        )

        if organization_exists:
            logging.info("organization creation failed due to duplicate entry")
            return (
                jsonify({"error": "An organization of the same name already exists"}),
                400,
            )
        # creating organization post all the validations
        organization = OrganizationModel(request_data)
        organization.save()
        return jsonify({"message": "organization created successfully"}), 200

    except Exception as err:
        logging.exception(
            "POST request to create organization failed due to the following error:%s",
            err,
        )
        return jsonify({"error": "something went wrong"}), 400


@organization_blueprint.route("/update", methods=["PUT"])
@jwt_required()
def update_organization():
    """
    PUT API to update an organization
    Reqest requires:
        - method: PUT
        - JWT Bearer token in Authorization header
        - body data:
            {
                "id" : organization_id (integer),
                "name": string(optional),
                "description": string(optional),
                "contact_email_id": valid email string (optional)
            }
    Response:
        - success message with status code 200 if everything is successful
        - error message with status code 400 and message "something went wrong"
            if anything goes wrong due to unknown reasons
        - error message with status code 404 with message "organization not found"
            if the organization does not exist
        - error message with status code 400 if an existing new name is provided
        - error message with status code 401
            if somebody without access to the organization hits the api
    """
    try:
        request_data = request.json
        user = get_current_user()
        logging.info(
            "PUT request to update organization by user:%s with payload:%s",
            user.id,
            request_data,
        )
        organization_id = request_data.get("id")
        organization = OrganizationModel.query.get(organization_id)
        if not organization:
            logging.info("PUT request failed as no such organization exists.")
            return jsonify({"error": "No such organization exists"}), 404

        if (
            not has_access_to_organization(organization_id=organization.id, user=user)
            and user.is_super_admin
        ):
            logging.info("PUT request failed due to unauthorised access")
            return (
                jsonify({"error": "Unauthorized access to organization functions"}),
                401,
            )
        if request_data.get("name"):
            if OrganizationModel.does_organization_exist(
                organization_name=request_data.get("name")
            ):
                return jsonify(
                    {
                        "error": "an organization of the same name exists,use another name"
                    }
                )
            organization.name = request_data.get("name")

        organization.description = (
            request_data.get("description")
            if request_data.get("description")
            else organization.description
        )
        organization.contact_email_id = (
            request_data.get("contact_email_id")
            if request_data.get("contact_email_id")
            else organization.contact_email_id
        )
        organization.update({"modified_by": user.id})
        logging.info("organization updated sucessfully")
        return jsonify({"message": "organization updated successfully!"}), 200
    except Exception as err:
        logging.exception("PUT request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"}), 400


@organization_blueprint.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_organization():
    """
    DELETE route to delete an organization
    Request Requiers:
    - method: DELETE
        - JWT Bearer token in Authorization header
        - body data:
            {
                "organization" : organization_id (integer)
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
        request_data = request.json
        user = get_current_user()
        logging.info(
            "DELETE request to delete organization by user:%s with payload:%s",
            user.id,
            request_data,
        )
        organization_id = request_data.get("organization_id")
        if not isinstance(organization_id, int):
            logging.exception("DELETE request failed due to faulty input")
            return jsonify({"error": "faulty input"}), 400

        organization = OrganizationModel.query.get(organization_id) or None
        if not organization:
            logging.info("DELETE request failed as no such organization exists")
            return jsonify({"error": "organization not found"}), 404

        if not has_access_to_organization(organization_id=organization_id, user=user):
            logging.info("DELETE request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": "Unauthorized access, you do not have the \
                            rights to delete this organization"
                    }
                ),
                401,
            )
        organization.delete()
        logging.info("organization deleted sucessfully")
        return jsonify({"message": "organization deleted successfully"}), 200
    except Exception as err:
        logging.exception("DELETE request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"}), 400
