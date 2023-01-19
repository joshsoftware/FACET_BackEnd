import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_current_user, jwt_required
from app.models.organization_model import OrganizationModel, OrganizationSchema
from app.models.user_model import UserModel, UserSchema

super_admin_blueprint = Blueprint("super_admin", __name__)


@super_admin_blueprint.route("/organizations/all", methods=["GET"])
@jwt_required()
def get_all_organizations():
    """
    GET request route to fetch all organization
    """
    try:
        user = get_current_user()
        if not (user.user_organization == 1 and user.is_super_admin is True):
            logging.info("GET request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": "unauthorised access, you do not possess the rights to this route"
                    }
                ),
                401,
            )
        organizations = OrganizationModel.get_all_organizations()
        #Make sure that the default organization is always having the id 1
        organizations.remove(OrganizationModel.get_one_organization(organization_id=1))
        return jsonify({"organizations": organizations}), 200
    except Exception as err:
        logging.exception("GET request failed due to the following error: %s", err)
        return jsonify({"error": "something went wrong"}), 400


@super_admin_blueprint.route("/members/all", methods=["GET"])
@jwt_required()
def get_all_members():
    """
    GET request route to fetch all members
    """
    try:
        super_admin_user = get_current_user()
        if not (
            super_admin_user.user_organization == 1
            and super_admin_user.is_super_admin is True
        ):
            logging.info("GET request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": "unauthorised access, you do not possess the rights to this route"
                    }
                ),
                401,
            )
        users = UserModel.get_all_members()
        users.remove(UserModel.get_user_profile(user=super_admin_user))
        for user in users:
            user['user_organization'] = OrganizationModel.get_one_organization(
                organization_id=user['user_organization']
            )
        return jsonify({"users": users}), 200
    except Exception as err:
        logging.exception("GET request failed due to the following error: %s", err)
        return jsonify({"error": "something went wrong"}), 400


@super_admin_blueprint.route("/organizations/members", methods=["GET"])
@jwt_required()
def get_organization_members():
    """
    GET request route to fetch members of one organization
    Request requires:
        - org_id
    """
    try:
        user = get_current_user()
        if not (user.user_organization == 1 and user.is_super_admin is True):
            logging.info("GET request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "error": "unauthorised access, you do not possess the rights to this route"
                    }
                ),
                401,
            )
        organization = OrganizationModel.get_one_organization(
            organization_id=request.args.get("org_id")
        )
        org_users = OrganizationModel.get_org_members(organization_id=organization['id'])
        return jsonify({"organization": organization, "org_members": org_users}), 200
    except Exception as err:
        logging.exception("GET request failed due to the following error: %s", err)
        return jsonify({"error": "something went wrong"}), 400
