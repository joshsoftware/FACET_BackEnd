from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from marshmallow import ValidationError

from . import jwt
from app.helpers.utils import get_current_user, get_project_members_id, is_super_admin
from app.models.UserModel import UserModel, UserSchema

auth_blueprint = Blueprint('auth', __name__)
user_schema = UserSchema()


@jwt.user_lookup_loader
def _user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]

    user = UserModel.get_one_user(identity)
    if user is None:
        return None
    # del user.password
    return user


# create account
@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    """
    Route to register user
    Requires:
        - method: POST
        - body data:
            {
                name: email,
                email: string,
                password: string
            }
    Response:
        - if success JSON response containing message with 201 code
            e.g. { message: "User Created Successfully!" }
        - if fails JSON response containing error message with 400 code
            e.g. {error: string or array or dict}
    """
    req_data = request.json

    try:
        data = user_schema.load(req_data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    user_exist = UserModel.get_user_by_email(data.get('email'))
    if user_exist:
        return jsonify({"error": "User already exist, please supply another email address"}), 400

    user = UserModel(data)
    user.save()
    return jsonify({"message": "User Created Successfully!"}), 201


# Login Account
@auth_blueprint.route('/login', methods=['POST'])
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
    req_data = request.json
    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    if not req_data.get('email') or not req_data.get('password'):
        return jsonify({"error": "Email and Password are required fields!"}), 400

    user = UserModel.get_user_by_email(data.get('email'))

    if not user:
        return jsonify({"error": "Invalid Credentials!"}), 400

    if user and user.check_hash(data.get('password')):
        access_token = create_access_token(identity=user.id)
        resfresh_token = create_refresh_token(identity=user.id)
        return jsonify({"access_token": access_token, "refresh_token": resfresh_token, "user": UserModel.get_user_profile(user)}), 200

    return jsonify({"error": "Invalid Credentials!"}), 400


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
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200


@auth_blueprint.route('/delete/', methods=['DELETE'])
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
    req_data = request.json
    super_admin = get_current_user().id
    try:
        user = UserModel.get_one_user(req_data.get('user'))
    except Exception as err:
        return jsonify({"error": str(err)}), 400

    if not user:
        return jsonify({"error": "No such user exists"}), 404

    if not is_super_admin(super_admin):
        return jsonify({"error": "Sorry you do not possess the super admin rights to delete a user"}), 401

    user.delete()

    return jsonify({"message": "User deleted sucessfully"}), 200


@auth_blueprint.route('/add_admins', methods=['POST'])
@jwt_required()
def add():
    """
    Route which gives access to superadmin to add users
    Requires:
        - method: POST
        - JWT Bearer token in Authorization header
        - body data:
            {
                admin: array of users id
            }
    Response:
        - if success JSON response containing message with 200 code
            e.g. {message: string}
        - if fails JSON response containing error message with 400 code
            e.g. {error: string}
    """
    req_data = request.json
    user = get_current_user()

    if not is_super_admin(user.id):
        return jsonify({"error": "You do not possess the super admin rights to add modify a user status"}), 401

    try:
        admins = req_data['admin']
        del req_data['admin']
        if admins:
            for admin_id in admins:
                member = UserModel.get_one_user(admin_id)
                member.is_admin = True
                member.update()
            return jsonify({"message": "Members successfully updated to admin"}), 200
    except Exception as err:
        # add logger
        print(err)
        return jsonify({"error": "Something went wrong!"}), 400


@auth_blueprint.route('/get_all_users', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Route which gives users list
    Requires:
        - method: GET
        - JWT Bearer token in Authorization header
        - params: 
            {
                exclude: 'admins' or 'projectMembers' or None,
                project: "string, required if exclude == 'projectMembers'"
            }
    Response:
        - if success JSON response containing message with 200 code
            e.g. { users: array of users data e.g. [{ ...user_data }] }
        - if fails JSON response containing error message with 400 code
            e.g. {error: string}
    """
    exclude = request.args.get('exclude')
    project = request.args.get('project')
    user = get_current_user()

    try:
        users = UserModel.get_all_members()

        if exclude == 'admins':
            if not is_super_admin(user.id):
                return jsonify({
                    "error": "You do not possess the super admin rights to access all the users of the organization"
                }), 401
            users = [user for user in users if not user['is_admin']]
        elif exclude == 'projectMembers':
            project_members = get_project_members_id(project)
            users = [user for user in users if user['id']
                     not in project_members]

        return jsonify({"users": users}), 200
    except Exception as err:
        # add logger
        print(err)
        return jsonify({"error": "Something Went Wrong!"}), 400
