from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TeststepModel import TestStepModel
from app.models.TestdataModel import TestdataModel, TestdataSchema

testdata_blueprint = Blueprint('testdata', __name__)
testdata_schema = TestdataSchema()


@testdata_blueprint.route("/",methods = ["GET"])
@testdata_blueprint.route("/<string:id>",methods = ["GET"])
@jwt_required()
def getTestdata(id=0):
    try:
        teststep_id = request.args.get("teststep")
        if id!=0:
            data = TestdataModel.get_one_testdata(id)
            return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

        data = TestdataModel.get_all_testdatas(teststep_id)
        return jsonify({"testdata": data}), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as e:
        return jsonify(e), 400


@testdata_blueprint.route("/new",methods = ["POST"])
@jwt_required()
def createTestdata():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get('name'))
    user = get_current_user()
    req_data['created_by'] = user.id
    req_data['modified_by'] = user.id
    try:
        data = testdata_schema.load(req_data)
    except ValidationError as err:
        return jsonify(str(err)), 400

    is_exist = TestdataModel.is_exist(data.get('name'), data.get('teststep'))

    if is_exist:
        return jsonify({"error": "You already have a Testdata of the same name in this Teststep."}), 400

    testdata = TestdataModel(data)
    testdata.save()
    return jsonify({"success": "Testdata created successfully!"}), 201

@testdata_blueprint.route("/update",methods=["PUT"])
@jwt_required()
def update_Testdata():
    req_data = request.json
    try:
        testdata = req_data.get('id')
        testdata = TestdataModel.query.get(testdata)
        user = get_current_user()
        if testdata:
            teststep = TestStepModel.query.filter_by(id = testdata.teststep).first()
            project = int(str(teststep.project)[3:-1])
            if has_access_to_project(project,user.id):
                if req_data.get('name'):
                    name = req_data.get('name')
                    testdata.name = name
                if req_data.get('payload'):
                    payload = req_data.get('payload')
                    testdata.payload = payload
                if req_data.get('expected_outcome'):
                    expected_outcome = req_data.get('expected_outcome')
                    testdata.expected_outcome = expected_outcome
                testdata.update({'modified_by' : user.id})
            else:
                return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"}),401
        else:
            return jsonify({"Error" : "No such Testdata exists"}),404
    except Exception as err:
        return jsonify(str(err)),400
    return jsonify({"Success" : "Testdata Updated successfully"}),200


"""
API payload format:
{
    "testdata" : id(int)
}
"""
@testdata_blueprint.route("/delete/",methods=["DELETE"])
@jwt_required()
def delete_testdata():
    req_data = request.json
    user = get_current_user()
    try:
        testdata = TestdataModel.query.get(req_data.get('testdata'))
    except Exception as e:
        return jsonify(str(e)),400
    if testdata:
        teststep_id = testdata.teststep
        project_id = TestStepModel.query.get(teststep_id).project_id
        if has_access_to_project(project_id,user.id):
            testdata.delete()
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}),401
    else:
        return jsonify({"error" : "No such Testdata exists"}),404
    return jsonify({"Success" : "Testdata deleted successfully"}),200