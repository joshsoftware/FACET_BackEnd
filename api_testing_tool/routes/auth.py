from datetime import datetime
from flask import Blueprint, jsonify, request
from api_testing_tool import db, jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


auth_blueprint = Blueprint('auth', __name__)

@jwt.user_lookup_loader
def _user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    print(identity)
    user = db.users.find_one({"email":identity})
    if user is None:
        return None
    user['_id'] = str(user['_id'])
    del user['password']
    return user


# create account
@auth_blueprint.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if len(email)<6:
        return jsonify({"errors":{"email":"Email Should be 6 characters Long"}})
    if len(password)<4:
        return jsonify({"errors":{"password":"Password Should be 4 characters Long"}})
    
    user = db.users.find_one({"email":email})

    if not user:
        user = db.users.insert_one({
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

    if not email or not password:
        return jsonify({"errors":"Email and Password Required"}), 400

    user = db.users.find_one({"email":email})
    
    if user and check_password_hash(user["password"], password):
        token = create_access_token(identity=user["email"])
        return jsonify({"token":token}), 200

    return jsonify({"error": "Invalid Credentials!"}), 400
