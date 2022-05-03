from datetime import datetime
from flask import Blueprint, jsonify, request
from api_testing_tool import db, jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from api_testing_tool.helpers import create_id, validation_error
from jsonschema import ValidationError, validate
from api_testing_tool.schema import signup_schema, login_schema

auth_blueprint = Blueprint('auth', __name__)

@jwt.user_lookup_loader
def _user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    
    user = db.users.find_one({"email":identity})
    if user is None:
        return None
    del user['password']
    return user


# create account
@auth_blueprint.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        validate(data, signup_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    user = db.users.find_one({"email":email})
    
    if not user:
        user = db.users.insert_one({
            "_id": create_id(),
            **data,
            "password": generate_password_hash(password),
            "joinedAt": datetime.now()
        })
        return jsonify({"message":"Account Created Successfully!"}), 201

    return jsonify({"errors":"User With this email already exists!"}), 400


# Login Account
@auth_blueprint.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        validate(data, login_schema)
    except ValidationError as e:
        error = validation_error(e)
        return jsonify(error), 400

    user = db.users.find_one({"email":email})
    
    if user and check_password_hash(user["password"], password):
        token = create_access_token(identity=user["email"])
        return jsonify({"token":token, "user": user['name']}), 200

    return jsonify({"error": "Invalid Credentials!"}), 400
