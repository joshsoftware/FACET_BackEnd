from crypt import methods
from flask import Blueprint, jsonify, request
from . import jwt
from flask_jwt_extended import create_access_token,jwt_required
from app.helpers.utils import get_current_user, is_super_admin
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


# Login Account
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

@auth_blueprint.route('/delete', methods=['POST'])
@jwt_required()
def delete_user():
    req_data = request.json
    super_admin = get_current_user().id
    try:
        user = UserModel.get_one_user(req_data.get('user'))
    except Exception as e:
        return jsonify(str(e)),400
    if user:
        if is_super_admin(super_admin):
            user.delete()
        else:
            return jsonify({"Error" : "Sorry you do not possess the super admin rights to delete a user"}),401
    else:
        return jsonify({"Error" : "No such user exists"}),404
    return jsonify({"success" : "User deleted sucessfully"}),200

'''
The below API provides the functionality of adding both members and admins
This functionality currently is only provisional for the super admin, and is out of bounds for normal users
Input :
    JWT token for authorisation
    admin -> input list, optional in nature, required to be interger in nature
'''
@auth_blueprint.route('/add',methods=['POST'])
@jwt_required()
def add():
    req_data = request.json
    user = get_current_user()
    if UserModel.is_super_user(user.id):
        try:
            admins = req_data['admin']
            del req_data['admin']
            if admins:
                for id in admins:
                    member = UserModel.get_one_user(id)
                    member.is_admin = True
                    member.update()
                return jsonify({"Success" : "Members successfully updated to admin"}),201
        except Exception as e:
            return jsonify(str(e)),400
    else:
        return jsonify({'Error' : 'You do not possess the super admin rights to add modify a user status'}),401