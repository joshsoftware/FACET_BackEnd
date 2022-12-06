from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TeststepModel import TestStepModel
from app.models.TestdataModel import TestdataModel, TestdataSchema
import logging

testdata_blueprint = Blueprint('testdata', __name__)
testdata_schema = TestdataSchema()


@testdata_blueprint.route("/", methods=["GET"])
@testdata_blueprint.route("/<string:id>", methods=["GET"])
@jwt_required()
def getTestdata(id=0):
    try:
        teststep_id = request.args.get("teststep")
        logging.info(f"GET request to fetch testdata by user:{get_current_user().id} with params:{dict(request.args)} and url:{request.url}")
        if id != 0:
            data = TestdataModel.get_one_testdata(id)
            logging.info(f"GET request successful, testdata returned successfully for testdata id:{id}")
            return jsonify(data), 200

        data = TestdataModel.get_all_testdatas(teststep_id)
        logging.info(f"GET request successful, testdatas returned successfully for teststep id:{teststep_id}")
        return jsonify({"testdata": data}), 200
    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@testdata_blueprint.route("/new", methods=["POST"])
@jwt_required()
def createTestdata():
    try:
        req_data = request.json
        req_data['name'] = create_slug(req_data.get('name'))
        user = get_current_user()
        logging.info(f"POST request to create testdata by user:{user.id} with payload:{req_data}")
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        try:
            data = testdata_schema.load(req_data)
        except ValidationError as err:
            logging.error(f"testdata creation failed due to the following error {err}")
            return jsonify({"error": str(err)}), 400

        is_exist = TestdataModel.is_exist(data.get('name'), data.get('teststep'))

        if is_exist:
            logging.info(f"testdata creation failed due to duplicate entry")
            return jsonify({"error": "You already have a Testdata of the same name in this Teststep."}), 400

        testdata = TestdataModel(data)
        testdata.save()
        logging.info(f"testdata created successfully")
        return jsonify({"message": "Testdata created successfully!"}), 201
    except Exception as err:
        logging.exception(f"POST request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@testdata_blueprint.route("/update", methods=["PUT"])
@jwt_required()
def update_Testdata():
    try:
        req_data = request.json
        testdata = req_data.get('id')
        testdata = TestdataModel.query.get(testdata)
        user = get_current_user()
        logging.info(f"PUT request to update testdata by user:{user.id} with payload:{req_data}")
        if not testdata:
            logging.info(f"PUT request failed as no such testdata exists for the project")
            return jsonify({"error": "No such Testdata exists"}), 404

        teststep = TestStepModel.query.filter_by(id=testdata.teststep).first()
        project = int(str(teststep.project)[3:-1])

        if not has_access_to_project(project, user.id):
            logging.info(f"PUT request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        testdata.name = create_slug(req_data.get('name')) if req_data.get('name') else testdata.name

        testdata.payload = req_data.get('payload') if req_data.get('payload') else testdata.payload

        testdata.expected_outcome = req_data.get('expected_outcome') if req_data.get('expected_outcome') else testdata.expected_outcome

        testdata.update({'modified_by': user.id})
        logging.info(f"testdata updated sucessfully")
        return jsonify({"message": "Testdata Updated successfully"}), 200
    except Exception as err:
        logging.exception(f"PUT request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


"""
API payload format:
{
    "testdata" : id(int)
}
"""


@testdata_blueprint.route("/delete/", methods=["DELETE"])
@jwt_required()
def delete_testdata():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(f"DELETE request to delete testdata by user:{user.id} with payload:{req_data}")
        try:
            testdata = TestdataModel.query.get(req_data.get('testdata'))
        except Exception as err:
            logging.exception(f"DELETE request failed due to the following error:{err}")
            return jsonify({"error": "something went wrong"}), 400
        if not testdata:
            logging.info(f"DELETE request failed as no such testdata exists for the project")
            return jsonify({"error": "No such Testdata exists"}), 404

        teststep_id = testdata.teststep
        project_id = TestStepModel.query.get(teststep_id).project_id
        if not has_access_to_project(project_id, user.id):
            logging.info(f"DELETE request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401

        testdata.delete()
        logging.info(f"testdata deleted sucessfully")
        return jsonify({"message": "Testdata deleted successfully"}), 200
    except Exception as err:
        logging.exception(f"DELETE request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400
