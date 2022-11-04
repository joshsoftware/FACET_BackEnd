from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TestsuiteModel import TestsuiteModel, TestsuiteSchema
from app.models.TestcaseModel import TestcaseModel

testsuite_blueprint = Blueprint('testsuites', __name__)
testsuite_schema = TestsuiteSchema()


@testsuite_blueprint.route('/', methods=["GET"])
@testsuite_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getTestsuites(id=0):
    """
    GET Request API for testsuites
    Requires:
        - method: GET
        - JWT Bearer token in Authorization header
        - Project name in params
    Response:
        - Error message with status code 400 if anything goes wrong due to faulty json or other unknown factors,
        - Error message with status code 401 if anybody without project access tries hit the API
        - If success, then json response with status code 200, where json look like :
            {"testsuites": list of dicitonaries}
    """
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"))
        if not has_access_to_project(project_id=project, user_id=user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

        if id != 0:
            data = TestsuiteModel.get_one_testsuite(id=id)
            return jsonify(data), 200

        data = TestsuiteModel.get_all_testsuites(project=project)
        return jsonify({"testsuites": data}), 200

    except Exception as err:
        print(str(err))
        return jsonify({"error": "Something went wrong"}), 400


@testsuite_blueprint.route('/new', methods=["POST"])
@jwt_required()
def createTestsuites():
    """"
    Route for creating a new testsuite
    Requires:
        - method : POST
        - JWT Bearer token in Authorization header
        - body data: 
            {
                name: string,
                project: string,
                array_of_testcases: array of integers, eg: [1,2,3]
            }
    Response:
        - if successful, then a json message of success with status code 200
        - error message with status code 401 if somebody without the acccess to project hits the api
        - error message with status code 400, with the message 'the testsuite already exists' if it already exists
        - error message with status code 400 and message 'something went wrong' if faulty input of any sort is provided
    """
    req_data = request.json
    req_data['project'] = get_project_id(slug=req_data.get("project"))
    req_data['name'] = create_slug(req_data.get("name"))
    user = get_current_user()
    req_data['created_by'] = user.id
    req_data['modified_by'] = user.id
    testcases = req_data.get('array_of_testcases')
    if not testcases:
        return jsonify({"error":"Testcases missing"}), 400
    del req_data['array_of_testcases']

    if not has_access_to_project(project_id=req_data['project'], user_id=user.id):
        return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401

    try:
        data = testsuite_schema.load(req_data)
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400

    is_exist = TestsuiteModel.is_exist(
        name=data.get('name'), project=data.get('project'))

    if is_exist:
        return jsonify({"error": "You already have a testsuite of the same name in this project."}), 400

    testsuite = TestsuiteModel(data)
    for testcase in testcases:
        testsuite.testcases.append(TestcaseModel.query.get(testcase))
    testsuite.save()
    return jsonify({"message": "testcase created with the given testsuites"}), 200


@testsuite_blueprint.route('/delete', methods=["DELETE"])
@jwt_required()
def deleteTestsuiets():
    """
    DELETE request API for deleting a testsuite
    Requires:
        - method: DELETE
        - JWT Bearer token in Authorization header
        - body data: 
            {
                "testsuite" : testsuite_id (integer)
            }
    Response:
        - success message with status code 200 if everything is successful
        - error message with status code 400 and message "faulty input" if faulty inputs are provided
        - error message with status code 404 and message "testsuite not found" if the testsuite does not exist
        - error message with status code 401 if somebody without access to the project hits the api 
    """
    req_data = request.json
    user = get_current_user()
    testsuite = req_data.get('testsuite')
    if not type(testsuite) is int:
        return jsonify({"error": "faulty input"}), 400

    testsuite = TestsuiteModel.query.get(testsuite) or None
    if not testsuite:
        return jsonify({"error": "testsuite not found"}), 404

    if not has_access_to_project(project_id=testsuite.project, user_id=user.id):
        return jsonify({"error": "You do not have access to this project, kindly connect to project admin to access the project components"}), 401
    testsuite.delete()
    return jsonify({"message": "testsuite deleted successfully"}), 200


@testsuite_blueprint.route('/update', methods=["PUT"])
@jwt_required()
def updateTestsuites():
    """
    PUT request API for updating testsuite
    Requires:
        - method: PUT
        - JWT Bearer token in Authorization header
        - body data: 
            {
                "id" : testsuite_id (integer),
                "array_of_testcases" : array of testcase_id, eg -> [1,2,7] 
            }
    Response:
        - success message with status code 200 if everything is successful
        - error message with status code 400 and message "something went wrong" if anything goes wrong due to unknown reasons
        - error message with status code 400 and message "you cannot delete all the testcases from the testsuite...." if an empty array of testcases is provided or no arguemnent of array of testcases is not provided
        - error message with status code 404 and message "testsuite not found" if the testsuite does not exist
        - error message with status code 401 if somebody without access to the project hits the api 
    """
    req_data = request.json
    user = get_current_user()
    try:
        testsuite = req_data.get('id')
        testsuite = TestsuiteModel.query.get(testsuite)
        if not testsuite:
            return jsonify({"error": "no such testsuite exists"}), 404

        if not has_access_to_project(project_id=testsuite.project, user_id=user.id):
            return jsonify({"error": "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}), 401

        if not req_data.get('array_of_testcases'):
            return jsonify({"error": "you cannot delete all the testcases from the testsuite, atleast 1 testcase is required to update the testsuite"}), 400

        testcases = req_data.get('array_of_testcases')
        testsuite.testcases.clear()
        for testcase in testcases:
            testsuite.testcases.append(TestcaseModel.query.get(testcase))

        testsuite.update({'modified_by': user.id})

        return jsonify({"message": "Testsuite Updated successfully"}), 200

    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400
