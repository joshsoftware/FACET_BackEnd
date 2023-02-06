"""
organization API module for
performing CRUD operations, adding and removing
both admins and members within an organization
"""
import os
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from flask import Blueprint, request, jsonify
from jinja2 import Environment
from flask_jwt_extended import get_current_user, jwt_required, create_access_token
from marshmallow import ValidationError
from app.helpers import create_slug
from app.helpers.utils import has_access_to_organization
from app.helpers.emails import signup_notification_email
from app.helpers.email_contents import mail_html_content
from app.models.organization_model import OrganizationModel, OrganizationSchema
from app.models.user_model import UserModel, UserSchema

organization_blueprint = Blueprint("organizations", __name__)
organization_schema = OrganizationSchema()

scheduler = BackgroundScheduler({"apscheduler.timezone": "Asia/Calcutta"})
scheduler.add_jobstore("sqlalchemy", url=os.getenv("DATABASE_URL"))
scheduler.start()

@organization_blueprint.route("/", methods=["GET"])
@organization_blueprint.route("/<int:org_id>", methods=["GET"])
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
        logging.info("GET request to fetch organization details by user: %s", user.id)
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
                        "error": "Unauthorised access,you do not have access to this organization"
                    }
                ),
                401,
            )
        organization = OrganizationModel.get_one_organization(organization_id=org_id)
        organization["is_org_superadmin"] = user.is_super_admin
        organization["is_admin"] = user.is_admin
        logging.info(
            "GET request to fetch details for organization:%d successfull by user:%s",
            org_id,
            user.name,
        )
        return jsonify({"organization": organization}), 200
    except Exception as err:
        logging.exception("GET request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"}), 400


@organization_blueprint.route("/members", methods=["GET"])
@jwt_required()
def get_org_members():
    """
    GET request module to fetch organization
    Request Requires-
        -method GET
        -JWT Bearer token
        -Params:{
            organization: int,
            exclude : "admins" [optional field]
        }
    Response:
        -status 200, with a list of all members of the organization
            if "exclude param is not provided"
        -status 200 with a list of all members of the oganization,
            excluding admins, if "exclude" param is provided
    """
    try:
        user = get_current_user()
        org_users = OrganizationModel.get_org_members(
            organization_id=user.user_organization
        )
        logging.info(
            "GET request to fetch organization members by user:%s with params:%s",
            user.id,
            request.args,
        )
        if request.args.get("exclude") == "admins":
            if not user.is_super_admin:
                logging.info(
                    "GET request to fetch organization members failed due to unauthorised access"
                )
                return jsonify({"error": "unauthorised access"}), 401
            org_users = [user for user in org_users if not user["is_admin"]]
        logging.info(
            "GET request to fetch organization members for organization:%d successfull by user:%s",
            user.user_organization,
            user.name,
        )
        return jsonify({"members": org_users}), 200
    except Exception as err:
        logging.info("GET request failed due to the following error: %s", err)
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
        request_data = request.json
        user = get_current_user()
        logging.info(
            "POST request to create organization by user:%d with payload:%s",
            user.id,
            request.url,
        )
        request_data["name"] = create_slug(request_data["name"])
        # Validating if the request data is valid as per organization Schema
        try:
            request_data = organization_schema.load(request_data)
        except ValidationError as err:
            logging.error(
                "organization created failed due to the following error: %s", err
            )
            user.delete()
            return jsonify({"error": str(err)}), 400

        organization_exists = OrganizationModel.does_organization_exist(
            organization_name=request_data["name"]
        )

        if organization_exists:
            logging.info("organization creation failed due to duplicate entry")
            user.delete()
            return (
                jsonify({"error": "An organization of the same name already exists"}),
                400,
            )
        # creating organization post all the validations
        organization = OrganizationModel(request_data)
        organization.save()
        organization_data = organization_schema.dump(organization)
        user.user_organization = organization.id
        user.is_super_admin = True
        user.is_admin = True
        user.save()
        logging.info(
            "Organization creation successfull org_id:%s by user: %s",
            organization.id,
            user.id,
        )
        return (
            jsonify(
                {
                    "message": "organization created successfully",
                    "orgaization": organization_data,
                }
            ),
            200,
        )

    except Exception as err:
        logging.exception(
            "POST request to create organization failed due to the following error:%s",
            err,
        )
        user.delete()
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
            # checking if the name is changed or not
            if not create_slug(request_data.get("name")) == organization.name:
                # checking if the new name is available or not
                if OrganizationModel.does_organization_exist(
                    organization_name=request_data.get("name")
                ):
                    logging.info(
                        "PUT request to update the organization failed as the new name already exists"
                    )
                    return (
                        jsonify(
                            {
                                "error": "an organization of the same name exists, use another name"
                            }
                        ),
                        400,
                    )
                # since name is not taken, it gets updated
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
        organization_data = organization_schema.dump(organization)
        logging.info("organization updated sucessfully")
        return (
            jsonify(
                {
                    "message": "organization updated successfully!",
                    "organization": organization_data,
                }
            ),
            200,
        )
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
        organization = OrganizationModel.query.get(user.user_organization) or None
        if not organization:
            logging.info("DELETE request failed as no such organization exists")
            return jsonify({"error": "organization not found"}), 404

        if not user.is_super_admin:
            logging.info("DELETE request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": (
                            "Unauthorized access,you do not have the rights to delete this"
                            " organization"
                        )
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


@organization_blueprint.route("/members/register", methods=["POST"])
def add_members_to_organization():
    """
    POST route for adding members to organization
    Request Requirements:
        -email
        -password
        -name
        -username
        -org_id
    Response:
    """
    try:
        request_data = request.json
        logging.info(
            "POST request for user signup and registration along with addition to organization with"
            " payload:%s",
            request_data,
        )
        organization_id = request_data.pop("org_id", None)
        organization = (
            OrganizationModel.get_one_organization(organization_id=organization_id)
            or None
        )
        if organization is None:
            logging.error("organization created failed as organization does not exist")
            return (
                jsonify({"error": "invalid request,organization does not exist"}),
                400,
            )
        request_data["account_type"] = "organization"
        try:
            request_data = UserSchema().load(request_data)
        except ValidationError as err:
            logging.error(
                "organization created failed due to the following error: %s", err
            )
            return jsonify({"error": str(err)}), 400
        user_exist = UserModel.get_user_by_email(request_data.get("email"))
        if user_exist:
            logging.info(
                "user signup failed for %s as email already exists",
                request_data["name"],
            )
            return (
                jsonify(
                    {"error": "User already exist, please supply another email address"}
                ),
                400,
            )
        does_username_exist = UserModel.does_username_exist(
            username=request_data.get("username")
        )
        if does_username_exist:
            logging.info(
                "user signup failed for %s as username already exists",
                request_data["name"],
            )
            return (
                jsonify(
                    {
                        "error": "username is already taken, please supply another username"
                    }
                ),
                400,
            )
        user = UserModel(data=request_data)
        user.user_organization = organization["id"]
        user.save()
        logging.info(
            "POST request to onboard user successful, onboarded user_id: %s", user.id
        )
        sender_mail = current_app.config["MAIL_USERNAME"]
        password = current_app.config["MAIL_PASSWORD"]
        email_job = scheduler.add_job(
            func=signup_notification_email,
            trigger="date",
            args=[user.username, user.email, sender_mail, password, organization['name']],
        )
        return jsonify({"message": "user onboarded successfully"}), 200
    except Exception as err:
        logging.info("POST request failed due to the following error:%s", err)
        return jsonify({"error": "something went wrong"}), 400


@organization_blueprint.route("/members/remove", methods=["DELETE"])
@jwt_required()
def remove_members():
    """
    DELETE request to remove members permanently
    Request requires:
        - method: DELETE
        - JWT Bearer token in Authorization header
        - body data:
            {
                "user_id" : integer
            }
    """
    try:
        request_data = request.json
        user = get_current_user()
        logging.info(
            "DELETE request to remove user from organization by user:%s, with payload:%s",
            user.id,
            request_data,
        )
        if not user.is_super_admin:
            logging.info("DELETE request failed due to unauthorised access")
            return (
                jsonify({"error": "Unauthorized access to organization functions"}),
                401,
            )
        user_to_be_removed = UserModel.query.get(request_data.get("user_id"))
        organization = OrganizationModel.query.get(user.user_organization)
        organization.org_users.remove(user_to_be_removed)
        organization.save()
        user_to_be_removed.user_organization = 1
        user_to_be_removed.account_type = "personal"
        user_to_be_removed.save()
        logging.info(
            "DELETE to remove user from organization by user:%s successfull", user.id
        )
        return jsonify({"message": "user removed from organization successfully"}), 200
    except Exception as err:
        logging.info(
            "DELETE request to remove user failed due to the following error:%s", err
        )
        return jsonify({"error": "something went wrong"}), 400


@organization_blueprint.route("/members/update", methods=["PUT"])
@jwt_required()
def update_member_role():
    """
    PUT API to update the roles existing members of the organization
    Request Requires:
        - method: PUT
        - JWT Bearer token in Authorization header
        - body data:
            {
                member: “id”,
                updatedRole: “string”
            }

    """
    try:
        request_data = request.json
        user = get_current_user()
        logging.info(
            "PUT request to update user roles by user: %s with payload:%s",
            user.id,
            request_data,
        )
        organization = OrganizationModel.get_one_organization(
            organization_id=user.user_organization
        )
        if not organization:
            logging.info("PUT request faield as organization does not exist")
            return (
                jsonify({"error": "invalid request,organization does not exist"}),
                400,
            )
        if not user.is_super_admin:
            logging.info("PUT request failed due to unauthorised access")
            return jsonify({"error": "unauthorised access"}), 401
        member_to_update = UserModel.get_one_user(user_id=request_data.get("member"))
        new_role = request_data.get("updatedRole")
        if new_role == "admin":
            member_to_update.is_admin = True
            member_to_update.is_super_admin = False
        elif new_role == "member":
            member_to_update.is_admin = False
            member_to_update.is_super_admin = False
        member_to_update.save()
        logging.info("Role updated successfully for user: %s", member_to_update.id)
        return jsonify({"message": "role updated successfully"}), 200
    except Exception as err:
        logging.info(
            "PUT request to update user role failed due to the following error:%s", err
        )
        return jsonify({"error": "something went wrong"}), 400


@organization_blueprint.route("/members/invite", methods=["POST"])
@jwt_required()
def invite_members():
    """
    org id
    email
    POST request route to bulk invite users for organization
        - method : POST
        - JWT Bearer authentication token in the header
        - Request body:{
            invited_members: [list of emails of members to be invited]
        }
    """
    try:
        request_data = request.json
        user = get_current_user()
        organization = user.user_organization
        invited_members = request_data.get("invited_members")
        logging.info(
            "POST request to invite members via email by user:%s with payload:%s",
            user.id,
            request_data,
        )
        sender_email = current_app.config["MAIL_USERNAME"]
        password = current_app.config["MAIL_PASSWORD"]
        if not organization:
            logging.info(
                "POST request to send emails failed as organization does not exist"
            )
            return jsonify({"error": "something went wrong"}), 400

        # JSON for organization details
        organization = OrganizationModel.get_one_organization(
            organization_id=organization
        )
        uninvited_members = []
        for invited_member in invited_members:
            if UserModel.get_user_by_email(email=invited_member):
                uninvited_members.append(invited_member)
                logging.info(
                    "email inviation for user email:%s aborted as the user already exists",
                    invited_member,
                )
            else:
                token = create_access_token(
                    identity={
                        "organization_id": organization["id"],
                        "email_address": invited_member,
                    }
                )
                message = MIMEMultipart("alternative")
                message["Subject"] = "FACET Invitation"
                message["From"] = sender_email
                message["To"] = invited_member
                # html content recieved
                html_content = mail_html_content
                part1 = MIMEText(
                    Environment()
                    .from_string(html_content)
                    .render(
                        invite_sender_name=user.name,
                        invite_sender_organization=organization["name"],
                        signup_url=f"{current_app.config['FRONTEND_URL']}/organization/\
                            {organization['name']}/invitation?token={token}",
                        action_url=f"{current_app.config['FRONTEND_URL']}/organization/\
                            {organization['name']}/invitation?token={token}",
                    ),
                    "html",
                )
                # html content injected in the mail
                message.attach(part1)
                fp = open('media/images/logo.png', 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()
                msgImage.add_header('Content-ID', '<image1>')
                message.attach(msgImage)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(
                        sender_email,
                        invited_member,
                        message.as_string(),
                    )
                logging.info(
                    "invite user sent to the email:%s for organization:%s by sender:%s",
                    invited_member,
                    organization["id"],
                    sender_email,
                )
        logging.info("Email invites completed")
        return (
            jsonify(
                {
                    "success": "mails sent",
                    "uninvited_members": uninvited_members,
                    "uninvited_members_length": len(uninvited_members),
                }
            ),
            200,
        )
    except Exception as err:
        logging.info(
            "POST request to send mails failed due to the following err:%s", err
        )
        return jsonify({"error": "something went wrong"}), 400
