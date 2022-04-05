from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from api_testing_tool import db
from api_testing_tool.helpers.utils import create_id

testdata_blueprint = Blueprint('testdata', __name__)

@testdata_blueprint.route("/api/get_testdata",methods = ["GET"])
@jwt_required()
def getTestdata():
    data = request.json
    testcase_id = data.get("testcase_id")
    testcase_testdata = db.testdata.find({"testcase_id" : testcase_id})
    return jsonify(testcase_testdata)

@testdata_blueprint.route("/api/create-testdata",methods = ["POST"])
@jwt_required()
def createTestdata():
    data = request.json
    testcase_id = data.get("testcase_id")
    payload = data.get("payload")
    if testcase_id == "" or payload == "":
        return jsonify({"error" : "all the fields are to be filled mandatorily"})
    else:
        db.testdata.insert_one({
            "_id" : create_id(),
            "testcase_id" : testcase_id,
            "payload" : payload,
        })
        return jsonify({"success" : "testdata added successfully"})