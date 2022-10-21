from flask import Blueprint, jsonify, request
from app.models.UserModel import UserModel, UserSchema
from flask_jwt_extended import jwt_required, get_current_user

user_blueprint = Blueprint('user', __name__)
user_schema = UserSchema()

@user_blueprint.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    GET request for user profile
    Requires: JWT Bearer token in Authorization header
    """
    try:
        user = get_current_user()
        user = UserModel.get_user_profile(user)
        return jsonify({ "user": user }), 200
    except Exception as e:
        print(str(e))
        return jsonify({ "error": "Something Went Wrong!" }), 400

@user_blueprint.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Route to change password of user on users request
    Requires:
        - JWT Bearer token in Authorization header
        - body data: 
            {
                curr_password: string,
                new_password: string,
                con_new_password: string
            }
    Response:
        - if success JSON response containing message with 200 code
            e.g. {"message": "Password Changed Successfully!"}
        - if fails JSON response containing error message with 400 code
            e.g. {"error": "Something Went Wrong!"}
    """
    try:
        user = get_current_user()
        req_data = request.json

        curr_password = req_data.get('curr_password')
        new_password = req_data.get('new_password')
        con_new_password = req_data.get('con_new_password')

        if not curr_password or not new_password or not con_new_password:
            return jsonify({ "error": "All fields are required!" }), 400

        if new_password != con_new_password:
            return jsonify({ "error": "New Passwords not matched!" }), 400

        if user and user.check_hash(req_data.get('curr_password')):
            user.update(data={"password": new_password})
            return jsonify({ "message": "Password changed successfully!" }), 200
        else:
            return jsonify({ "error": "Invalid password!" }), 400
        pass
    except Exception as e:
        print(str(e), e)
        return jsonify({ "error": "Something Went Wrong!" }), 400

@user_blueprint.route('/profile/update', methods=['PATCH'])
@jwt_required()
def update_profile():
    """
    Route to update profile of user on users request
    Requires:
        - JWT Bearer token in Authorization header
        - body data: data to be updated
            e.g. {
                name: updatedName
            }
    Response:
        - if success JSON response containing message with 200 code
            e.g. {"message": "Profile Updated Successfully!", "user": {...user_data}}
        - if fails JSON response containing error message with 400 code
            e.g. {"error": "Something Went Wrong!"}
    
    """
    try:
        user = get_current_user()
        req_data = request.json

        # not update email
        if req_data.get('email'):
            del req_data['email']

        user.update(req_data)
        user = UserModel.get_user_info(user.id)
        return jsonify({ "message": "Profile updated successfully!", "user": user }), 200
    except Exception as e:
        print(e)
        return jsonify({ "error": "Something Went Wrong!" }), 400