"""
organization API module for
performing CRUD operations, adding and removing
both admins and members within an organization
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_current_user, jwt_required
from app.helpers import create_slug
from marshmallow import ValidationError
from app.models.organization_model import OrganizationModel, OrganizationSchema

organization_blueprint = Blueprint("organizations",__name__)
organization_schema = OrganizationSchema()

@organization_blueprint.route("/",methods=["GET"])
@jwt_required()
def get_organization_data():
    """
    GET request route for fetching data of a single
    organization
    """
    organization = request.url

@organization_blueprint.route("/new",methods=["POST"])
@jwt_required()
def create_organization():
    """
    POST request route for creating a new organization
    """
    request_data = request.json
    user = get_current_user().id