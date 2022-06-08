from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id
from app.models.TestcaseModel import TestcaseModel
from app.models.TestsuiteModel import TestsuiteModel, TestsuiteSchema

testsuite_blueprint = Blueprint('testsuites', __name__)
testsuite_schema = TestsuiteSchema()

@testsuite_blueprint.route('/', methods=["GET"])
@testsuite_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getTestsuites(id=0):
    try:
        if id!=0:
            data = TestsuiteModel.get_one_testsuite(id)
            return jsonify(data), 200
        project = get_project_id(request.args.get("project"))
        data = TestsuiteModel.get_all_testsuites(project)
        return jsonify({"testsuites": data}), 200
        
    except Exception as e:
        return jsonify(str(e)),400
    

@testsuite_blueprint.route('/new',methods = ["POST"])
@jwt_required()
def createTestsuites():
    req_data = request.json 
    req_data['project'] = get_project_id(req_data.get("project"))
    req_data['name'] = create_slug(req_data.get("name"))
    testcases = req_data.get('array_of_testcases')
    del req_data['array_of_testcases']

    try:
        data = testsuite_schema.load(req_data)
    except ValidationError as err:
        return jsonify(str(err)), 400


    is_exist = TestsuiteModel.is_exist(data.get('name'), data.get('project'))

    if is_exist:
        return jsonify({"error": "You already have a testcases of the same name in this project."}), 400

    testsuite = TestsuiteModel(data)
    for i in testcases:
        testsuite.testcases.append(TestcaseModel.query.get(i))
    testsuite.save()
    return jsonify({"success" : "testsuite created with the given testcases"})

@testsuite_blueprint.route('/delete',methods=["POST"])
@jwt_required()
def delete_testsuite():
    req_data = request.json
    try:
        testsuite = TestsuiteModel.query.get(req_data.get('testsuite'))
    except Exception as e:
        return jsonify(str(e))
    if testsuite:
        testsuite.delete()
    else:
        return jsonify({"error" : "No such testsuite exists"})
    return jsonify({"Success" : "testsuite deleted successfully"})

