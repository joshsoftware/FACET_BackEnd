from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TestdataModel import TestdataModel
from app.models.TeststepModel import TestStepModel
from app.models.TestcaseModel import TestcaseModel, TestcaseSchema
import logging

testcase_blueprint = Blueprint('testcases', __name__)
testcase_schema = TestcaseSchema()


@testcase_blueprint.route('', methods=["GET"])
@testcase_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getTestcases(id=0):
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"),user.user_organization)
        logging.info(
            f"GET request to fetch testcase by user:{user.id} with params:{dict(request.args)} and url:{request.url}")
        if not has_access_to_project(project, user.id):
            logging.info(f"GET request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id != 0:
            data = TestcaseModel.get_one_testcase(id)
            logging.info(
                f"GET request successful, testcase returned successfully for testcase id:{id}")
            return jsonify(data), 200
        data = TestcaseModel.get_all_testcases(project)
        logging.info(
            f"GET request successful, testcases returned successfully for project id:{project}")
        return jsonify({"testcases": data}), 200

    except Exception as err:
        logging.exception(
            f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@testcase_blueprint.route('', methods=["POST"])
@jwt_required()
def createTestcases():
    try:
        user = get_current_user()
        req_data = request.json
        req_data['project'] = get_project_id(req_data.get("project"),user.user_organization)
        req_data['name'] = create_slug(req_data.get("name"))
        logging.info(
            f"POST request to create testcase by user:{user.id} with payload:{req_data}")
        req_data['created_by'] = user.id
        req_data['modified_by'] = user.id
        teststeps = req_data.get('array_of_teststeps')
        del req_data['array_of_teststeps']

        if not has_access_to_project(req_data['project'], user.id):
            logging.info(f"POST request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        try:
            data = testcase_schema.load(req_data)
        except ValidationError as err:
            logging.error(
                f"testcase creation failed due to the following error {err}")
            return jsonify({"error": str(err)}), 400

        is_exist = TestcaseModel.is_exist(
            data.get('name'), data.get('project'))

        if is_exist:
            logging.info(f"testcase creation failed due to duplicate entry")
            return jsonify({"error": "You already have a testcase of the same name in this project."}), 400

        testcase = TestcaseModel(data)
        testcase.execution_sequence = ""
        for teststep in teststeps:
            testcase.teststeps.append(
                TestStepModel.query.get(teststep['teststep']))
            testcase.execution_sequence = testcase.execution_sequence + \
                str(teststep.get('teststep')) + ","
            for td in teststep['testdata']:
                testcase.testdatas.append(TestdataModel.query.get(td))
        testcase.save()
        logging.info(f"testcase created successfully")
        return jsonify({"message": "testcase created with the given teststeps"}), 200
    except Exception as err:
        logging.exception(
            f"POST request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@testcase_blueprint.route('', methods=["DELETE"])
@jwt_required()
def delete_testcase():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(
            f"DELETE request to delete testcase by user:{user.id} with payload:{req_data}")
        try:
            testcase = TestcaseModel.query.get(req_data.get('testcase'))
        except Exception as err:
            logging.exception(
                f"DELETE request failed due to the following error:{err}")
            return jsonify({"error": "something went wrong"}), 400

        if not testcase:
            logging.info(
                f"DELETE request failed as no such testcase exists for the project")
            return jsonify({"error": "No such testcase exists"}), 404

        if not has_access_to_project(testcase.project, user.id):
            logging.info(f"DELETE request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401

        testcase.delete()
        logging.info(f"testcase deleted sucessfully")
        return jsonify({"message": "testcase deleted successfully"}), 200
    except Exception as err:
        logging.exception(
            f"DELETE request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@testcase_blueprint.route('', methods=["PUT"])
@jwt_required()
def update_testcase():
    try:
        req_data = request.json
        user = get_current_user()
        logging.info(
            f"PUT request to update testcase by user:{user.id} with payload:{req_data}")
        testcase = req_data.get('id')
        testcase = TestcaseModel.query.get(testcase)
        if not testcase:
            logging.info(
                f"PUT request failed as no such testcase exists for the project")
            return jsonify({"error": "no such testcase exists"}), 404

        if not has_access_to_project(testcase.project, user.id):
            logging.info(f"PUT request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make updates in the project components"}), 401

        if type(req_data.get('name')) is str:
            name = req_data.get('name')
            testcase.name = name

        if type(req_data.get('description')) is str:
            description = req_data.get('description')
            testcase.description = description

        if req_data.get('array_of_teststeps'):
            teststeps = req_data.get('array_of_teststeps')
            
            are_teststeps_valid, message = teststeps_validator(
                array_of_teststeps=teststeps)

            if not are_teststeps_valid:
                logging.info(
                    f"PUT request to update testcases failed due to the following error:{message}")
                return jsonify({"error": message}), 400
                
            if len(teststeps) > 0:
                execution_sequence = ""
                testcase.teststeps.clear()
                testcase.testdatas.clear()
                for test_step in teststeps:
                    teststep = TestStepModel.query.get(
                        test_step["teststep"])
                    execution_sequence = execution_sequence + \
                        str(test_step["teststep"]) + ","
                    testcase.teststeps.append(teststep)
                    testcase.execution_sequence = execution_sequence
                    for td in test_step['testdata']:
                        testcase.testdatas.append(
                            TestdataModel.query.get(td))
        else:
            logging.info(
                f"PUT request failed as empty array of teststeps was provided")
            return jsonify({"error": "You cannot delete all the teststeps, atleast add one to update"}), 400

        testcase.update({'modified_by': user.id})
        logging.info(f"testcase updated sucessfully")
        return jsonify({"message": "Testcase Updated Successfully"}), 200
    except Exception as err:
        logging.exception(
            f"PUT request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


def teststeps_validator(array_of_teststeps):
    for teststep in array_of_teststeps:
        if type(teststep.get('teststep')) is not int:
            return False, "invalid payload provided, teststep id is not int"
        elif type(teststep.get('testdata')) is not list:
            return False, "invalid input format of testdata"
        elif not len(teststep.get('testdata')) > 0:
            return False, "zero testdata provided for the testcase"
    return True, ""
