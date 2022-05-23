from flask import Blueprint, jsonify, request
from . import jwt
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
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
    req_data = request.json

    try:
        data = user_schema.load(req_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_exist = UserModel.get_user_by_email(data.get('email'))
    if user_exist:
        return jsonify({'error':"User already exist, please supply another email address"}), 400
    
    user = UserModel(data)
    user.save()

    return jsonify({"message":"User Created Successfully!"}), 201


# # Login Account
@auth_blueprint.route('/login', methods=['POST'])
def login():
    req_data = request.json

    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as err:
        return jsonify(err), 400

    if not req_data.get('email') or not req_data.get('password'):
        return jsonify({"error": "Email and Password are required fields!"}), 400

    user = UserModel.get_user_by_email(data.get('email'))

    if not user:
        return jsonify({"error": "Invalid Credentials!"}), 400
    
    if user and user.check_hash(data.get('password')):
        token = create_access_token(identity=user.id)
        return jsonify({"token":token, "user": user.name}), 200

    return jsonify({"error": "Invalid Credentials!"}), 400
