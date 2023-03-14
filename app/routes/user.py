import logging
import os
from flask import Blueprint, jsonify, request
from app.models.user_model import UserModel, UserSchema
from flask_jwt_extended import jwt_required, get_current_user, create_access_token, decode_token
from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.helpers.emails import forgot_password_mail

scheduler = BackgroundScheduler({"apscheduler.timezone": "Asia/Calcutta"})
scheduler.add_jobstore("sqlalchemy", url=os.getenv("DATABASE_URL"))
scheduler.start()

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
        logging.info(f"GET request to fetch user details by user:{user.id} with params:{dict(request.args)} and url:{request.url}")
        user = UserModel.get_user_profile(user)
        return jsonify({ "user": user }), 200
    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}),400

@user_blueprint.route('/password', methods=['PUT'])
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
        logging.info(f"POST request to change password by user:{user.id} with payload:{req_data}")
        curr_password = req_data.get('curr_password')
        new_password = req_data.get('new_password')
        con_new_password = req_data.get('con_new_password')

        if not curr_password or not new_password or not con_new_password:
            logging.info(f"POST request to change password failed as all fields were not provided")
            return jsonify({ "error": "All fields are required!" }), 400

        if new_password != con_new_password:
            logging.info(f"POST request to change password failed as new passwords did not match")
            return jsonify({ "error": "New Passwords not matched!" }), 400

        if user and user.check_hash(req_data.get('curr_password')):
            user.update(data={"password": new_password})
            logging.info(f"password changed successfully")
            return jsonify({ "message": "Password changed successfully!" }), 200
        else:
            logging.info(f"POST request to change password failed as invalid password provided")
            return jsonify({ "error": "Invalid password!" }), 400
    except Exception as err:
        logging.exception(f"POST request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}),400

@user_blueprint.route('/profile', methods=['PATCH'])
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
        logging.info(f"POST request to update profile by user:{user.id} with payload:{req_data}")
        # not update email
        if req_data.get('email'):
            del req_data['email']

        user.update(req_data)
        user = UserModel.get_user_info(user.id)
        logging.info(f"profile updated successfully")
        return jsonify({ "message": "Profile updated successfully!", "user": user }), 200
    except Exception as err:
        logging.exception(f"PATCH request failed due to the following error:{err}")
        return jsonify({"error":"something went wrong"}),400

@user_blueprint.route('/password/forgot', methods=["POST"])
def forgot_password():
    """
    Route to update password in case the user forgets
    """
    try:
        req_data = request.json
        logging.info(f"POST request for forget password with request data:{req_data}")
        email_id = req_data['email_id']
        user_exists = UserModel.get_user_by_email(email=email_id)
        if not user_exists:
            logging.info(f"POST request for forgot password failed as user does not exist")
            return jsonify({"error": "user does not exist for the given email id"}), 400
        forgot_password_token = create_access_token(identity={"user_id": user_exists.id})
        email_data = {
            "sender_email": current_app.config["MAIL_USERNAME"],
            "reciever_email": email_id,
            "password": current_app.config["MAIL_PASSWORD"],
            "reset_password_url" : f"{current_app.config['FRONTEND_URL']}/forgot-password?token={forgot_password_token}"
        }
        email_job = scheduler.add_job(
                func=forgot_password_mail,
                trigger="date",
                args=[email_data],
            )
        return jsonify({"message": "email sent to the provided email id"}), 200
    except Exception as err:
        logging.exception(f"POST request for forgot password failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400

@user_blueprint.route('/password/reset', methods=["PATCH"])
@jwt_required(optional=True)
def reset_password():
    """
    Route to change password
    Requires
        body : {
            "new_password": string,
            "user_token": token
        }
    """
    try:
        req_data = request.json
        logging.info(f"PATCH request to reset password")
        new_password = req_data.get('new_password')
        user = decode_token(req_data.get('user_token'))['sub']['user_id']
        user = UserModel.query.get(user)
        user.update(data={"password": new_password})
        logging.info(f"PATCH request successful to reset password for user:{user.id}")
        return jsonify({"message": "password updated successfully"}), 200
    except Exception as err:
        logging.exception(f"POST request for reset password failed due to following error:{err}")
        return jsonify({"error": "something went wrong"}), 400
