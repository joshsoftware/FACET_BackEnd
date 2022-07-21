from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id,get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TestcaseModel import TestcaseModel
from app.models.TestsuiteModel import TestsuiteModel, TestsuiteSchema

testsuite_blueprint = Blueprint('testsuites', __name__)
testsuite_schema = TestsuiteSchema()

@testsuite_blueprint.route('/', methods=["GET"])
@testsuite_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getTestsuites(id=0):
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"))
        if has_access_to_project(project,user.id):
            if id!=0:
                data = TestsuiteModel.get_one_testsuite(id)
                return jsonify(data), 200
            data = TestsuiteModel.get_all_testsuites(project)
            return jsonify({"testsuites": data}), 200
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to access the project components"})
        
    except Exception as e:
        return jsonify(str(e)),400
    

@testsuite_blueprint.route('/new',methods = ["POST"])
@jwt_required()
def createTestsuites():
    req_data = request.json 
    req_data['project'] = get_project_id(req_data.get("project"))
    req_data['name'] = create_slug(req_data.get("name"))
    user = get_current_user()
    req_data['created_by'] = user.id
    req_data['modified_by'] = user.id
    testcases = req_data.get('array_of_testcases')
    del req_data['array_of_testcases']
    if has_access_to_project(req_data['project'],user.id):
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
    else:
        return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"})

@testsuite_blueprint.route('/delete',methods=["POST"])
@jwt_required()
def delete_testsuite():
    req_data = request.json
    user = get_current_user()
    try:
        testsuite = TestsuiteModel.query.get(req_data.get('testsuite'))
    except Exception as e:
        return jsonify(str(e))
    if testsuite:
        if has_access_to_project(testsuite.project,user.id):
            testsuite.delete()
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make deletions in the project components"})
    else:
        return jsonify({"error" : "No such testsuite exists"})
    return jsonify({"Success" : "testsuite deleted successfully"})

@testsuite_blueprint.route('/update',methods=["POST"])
@jwt_required()
def update_testsuite():
    req_data = request.json
    user = get_current_user()
    try:
        testsuite = req_data.get('id')
        testsuite = TestsuiteModel.query.get(testsuite)
        if testsuite:
            if has_access_to_project(testsuite.project,user.id):
                if req_data.get('name'):
                    name = req_data.get('name')
                    testsuite.name = name
                if req_data.get('description'):
                    description = req_data.get('description')
                    testsuite.description = description
                if req_data.get('environment'):
                    environment = req_data.get('environment')
                    testsuite.environment = environment
                if req_data.get('testcases'):
                    testsuite.testcases.clear()
                    testcases = req_data.get('testcases')
                    for i in testcases:
                        testcase = TestcaseModel.query.get(i)
                        testsuite.testcases.append(testcase)  
                testsuite.update({'modified_by' : user.id})
            else:
                return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"})
        else:
            return jsonify({"error" : "no such endpoint exists"})
    except Exception as err:
        return jsonify(str(err))
    return jsonify({"Success" : "Testsuite Updated Successfully"})

