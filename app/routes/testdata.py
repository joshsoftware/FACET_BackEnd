from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id
from app.models.TestdataModel import TestdataModel, TestdataSchema

testdata_blueprint = Blueprint('testdata', __name__)
testdata_schema = TestdataSchema()


@testdata_blueprint.route("/",methods = ["GET"])
@testdata_blueprint.route("/<string:id>",methods = ["GET"])
@jwt_required()
def getTestdata(id=0):
    try:
        testcase_id = request.args.get("testcase")
        if id!=0:
            data = TestdataModel.get_one_testdata(id)
            return jsonify(data), 200, {"content-type": "application/json; charset=UTF-8"}

        data = TestdataModel.get_all_testdatas(testcase_id)
        return jsonify({"testdata": data}), 200, {"content-type": "application/json; charset=UTF-8"}
    except Exception as e:
        return jsonify(e), 400


@testdata_blueprint.route("/new",methods = ["POST"])
@jwt_required()
def createTestdata():
    req_data = request.json
    req_data['name'] = create_slug(req_data.get('name'))
    
    try:
        data = testdata_schema.load(req_data)
    except ValidationError as err:
        return jsonify(str(err)), 400

    is_exist = TestdataModel.is_exist(data.get('name'), data.get('testcase'))

    if is_exist:
        return jsonify({"error": "You already have a Testdata of the same name in this Testcase."}), 400

    testdata = TestdataModel(data)
    testdata.save()
    return jsonify({"success": "Testdata created successfully!"}), 201

@testdata_blueprint.route("/update",methods=["POST"])
@jwt_required()
def update_Testdata():
    req_data = request.json
    try:
        testdata = req_data.get('id')
        testdata = TestdataModel.query.get('testdata')
        if testdata:
            if req_data.get('name'):
                name = req_data.get('name')
                testdata.name = name
            if req_data.get('payload'):
                payload = req_data.get('payload')
                testdata.payload = payload
            if req_data.get('expected_outcome'):
                expected_outcome = req_data.get('expected_outcome')
                testdata.expected_outcome = expected_outcome
            testdata.update()
        else:
            return jsonify({"Error" : "No such Testdata exists"})
    except Exception as err:
        return jsonify(str(err))
    return jsonify({"Success" : "Testdata Updated successfully"})