import os
from flask import Blueprint, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
)
from marshmallow import ValidationError
import logging
from . import jwt
from app.helpers.utils import get_current_user
from flask import current_app
from app.helpers.emails import signup_notification_email
from app.models.user_model import UserModel, UserSchema

auth_blueprint = Blueprint("auth", __name__)
user_schema = UserSchema()

scheduler = BackgroundScheduler({"apscheduler.timezone": "Asia/Calcutta"})
scheduler.add_jobstore("sqlalchemy", url=os.getenv("DATABASE_URL"))
scheduler.start()


@jwt.user_lookup_loader
def _user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]

    user = UserModel.get_one_user(identity)
    if user is None:
        return None
    # del user.password
    return user


# create account
@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    """
    Route to register user
    Requires:
        - method: POST
        - body data:
            {
                name: email,
                email: string,
                username: string,
                password: string,
                account_type: string
            }
    Response:
        - if success JSON response containing message with 201 code
            e.g. { message: "User Created Successfully!" }
        - if fails JSON response containing error message with 400 code
            e.g. {error: string or array or dict}
    """
    try:
        req_data = request.json
        # current_app.logger.info(f"User signup requested with name {req_data['name']} and email {req_data['email']}")
        logging.info(f"user signup requested with payload:{req_data}")
        try:
            data = user_schema.load(req_data)
        except ValidationError as err:
            logging.error(f"user signup failed due to the following error {err}")
            return jsonify({"error": err.messages}), 400

        user_exist = UserModel.get_user_by_email(data.get("email"))
        if user_exist:
            logging.info(
                f"user signup failed for {req_data['name']} as email already exists"
            )
            return (
                jsonify(
                    {"error": "User already exist, please supply another email address"}
                ),
                400,
            )
        does_username_exist = UserModel.does_username_exist(
            username=data.get("username")
        )
        if does_username_exist:
            logging.info(
                "user signup failed for %s as username already exists", req_data["name"]
            )
            return (
                jsonify(
                    {
                        "error": "username is already taken, please supply another username"
                    }
                ),
                400,
            )
        user = UserModel(data)
        user.save()
        if req_data.get("account_type") == "personal":
            user.user_organization = 1
            user.is_admin = True
            user.save()
            logging.info(f"user signup successful for {user.name}")
            sender_mail = current_app.config["MAIL_USERNAME"]
            password = current_app.config["MAIL_PASSWORD"]
            email_job = scheduler.add_job(
                func=signup_notification_email,
                trigger="date",
                args=[user.username, user.email, sender_mail, password, "personal"],
            )
            return jsonify({"message": "User Created Successfully!"}), 201
        else:
            access_token = create_access_token(identity=user.id)
            return jsonify({"access token": access_token}), 200
    except Exception as err:
        logging.exception(
            f"POST request for signup failed due to the following error: {err}"
        )
        return jsonify({"error": "something went wrong"}), 400


# Login Account
@auth_blueprint.route("/login", methods=["POST"])
def login():
    """
    Route to authenticate user with his credentials
    Requires:
        - method: POST
        - body data:
            {
                email: string,
                password: string
            }
    Response:
        - if success JSON response with 200 code
            e.g. {
                    user: { ...user_data },
                    token: string,
                    refresh_token: string
                }
        - if fails JSON response containing error message with 400 code
            e.g. {error: string or array or dict}
    """
    try:
        req_data = request.json
        logging.info(f"user login requested with payload {req_data}")
        try:
            data = user_schema.load(req_data, partial=True)
        except ValidationError as err:
            logging.info(f"login failed due to {err}")
            return jsonify({"error": err.messages}), 400

        if not req_data.get("email") or not req_data.get("password"):
            logging.info(
                f"user login failed failed as email or password weren't supplied"
            )
            return jsonify({"error": "Email and Password are required fields!"}), 400

        user = UserModel.get_user_by_email(data.get("email"))

        if not user:
            logging.info(f"User login failed as user does not exists")
            return jsonify({"error": "Invalid Credentials!"}), 400

        if user and user.check_hash(data.get("password")):
            access_token = create_access_token(identity=user.id)
            resfresh_token = create_refresh_token(identity=user.id)
            user_profile = UserModel.get_user_profile(user)
            logging.info(f"user login successful for {user.name}")
            is_facet_super_admin = (
                True if user.user_organization == 1 and user.is_super_admin else False
            )
            return (
                jsonify(
                    {
                        "access_token": access_token,
                        "refresh_token": resfresh_token,
                        "user": user_profile,
                        "is_facet_super_admin": is_facet_super_admin,
                    }
                ),
                200,
            )

        logging.info("user login failed due to invalid credentials")
        return jsonify({"error": "Invalid Credentials!"}), 400
    except Exception as err:
        logging.exception(
            f"POST request for signup failed due to the following error: {err}"
        )
        return jsonify({"error": "something went wrong"}), 400


@auth_blueprint.route("/token/refresh/", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Route to get new access_token using refresh_token
    Requires:
        - JWT Bearer token (Only Refresh Token) in Authorization header
    Response:
        - if success JSON response containing message with 200 code
            e.g. {"access_token": "token value"}
        - if token expires JSON response containing message with 401UNAUTHORIZED status code
            {"msg": "Token has expired"}
        - if signature verification fails JSON response containing message with
        422 UNPROCESSABLE ENTITY status code
            {"msg": "Signature verification failed"}
    """
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        logging.info(f"access token requested for user {identity}")
        return jsonify({"access_token": access_token}), 200
    except Exception as err:
        logging.exception(
            f"POST request for signup failed due to the following error: {err}"
        )
        return jsonify({"error": "something went wrong"}), 400


@auth_blueprint.route("/delete/", methods=["DELETE"])
@jwt_required()
def delete_user():
    """
    Route which gives access to superadmin to delete user
    Requires:
        - method: DELETE
        - JWT Bearer token in Authorization header
        - body data:
            {
                user: id
            }
    Response:
        - if success JSON response containing message with 200 code
            e.g. {message: "User deleted Successfully"}
        - if requested data not exist JSON response containing error message with 404 code
            e.g. {error: string}
        - if fails JSON response containing error message with 400 code
            e.g. {error: string}
    """
    try:
        req_data = request.json
        super_admin = get_current_user()
        logging.info(
            f"super admin request for deleting user with payload {req_data} and super_admin_id : {super_admin.id}"
        )
        try:
            user = UserModel.get_one_user(req_data.get("user"))
        except Exception as err:
            logging.exception(f"user deletion failed to the error:{err}")
            return jsonify({"error": str(err)}), 400

        if not user:
            logging.info(f"user deletion failed as no such user exists")
            return jsonify({"error": "No such user exists"}), 404

        if not super_admin.is_super_admin:
            logging.info(f"user deletion failed due to unauthorized access")
            return (
                jsonify(
                    {
                        "error": "Sorry you do not possess the super admin rights to delete a user"
                    }
                ),
                401,
            )

        user.delete()
        logging.info(f"user deleted successfully")
        return jsonify({"message": "User deleted sucessfully"}), 200
    except Exception as err:
        logging.exception(
            f"POST request for signup failed due to the following error: {err}"
        )
        return jsonify({"error": "something went wrong"}), 400


@auth_blueprint.route("/add_admins", methods=["POST"])
@jwt_required()
def add():
    """
    Route which gives access to superadmin to add users
    Requires:
        - method: POST
        - JWT Bearer token in Authorization header
        - body data:
            {
                admin: array of users id,
                organization : organization_id
            }
    Response:
        - if success JSON response containing message with 200 code
            e.g. {message: string}
        - if fails JSON response containing error message with 400 code
            e.g. {error: string}
    """
    req_data = request.json
    user = get_current_user()
    logging.info(f"request to add admins by user:{user.id} with req_data:{req_data}")
    if not user.is_super_admin:
        logging.info(f"request to add admins failed due to unauthorized access")
        return (
            jsonify({"error": "Unauthorized access"}),
            401,
        )
    try:
        admins = req_data["admin"]
        del req_data["admin"]
        if admins:
            for admin_id in admins:
                member = UserModel.get_one_user(admin_id)
                member.is_admin = True
                member.save()
            logging.info(f"members added successfully")
            return jsonify({"message": "Members successfully updated to admin"}), 200
    except Exception as err:
        logging.exception(
            f"request to add admins failed by user:{user} due to the following error:{err}"
        )
        return jsonify({"error": "Something went wrong!"}), 400
