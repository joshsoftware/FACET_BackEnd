from flask import Blueprint,jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.helpers import create_slug, get_project_id,get_current_user
from app.helpers.utils import has_access_to_project
from app.models.TestdataModel import TestdataModel
from app.models.TeststepModel import TestStepModel
from app.models.TestcaseModel import TestcaseModel, TestcaseSchema

testcase_blueprint = Blueprint('testcases', __name__)
testcase_schema = TestcaseSchema()

@testcase_blueprint.route('/', methods=["GET"])
@testcase_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getTestcases(id=0):
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"))
        if has_access_to_project(project,user.id):
            if id!=0:
                data = TestcaseModel.get_one_testcase(id)
                return jsonify(data), 200
            data = TestcaseModel.get_all_testcases(project)
            return jsonify({"testcases": data}), 200
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to access the project components"}),401
        
    except Exception as e:
        return jsonify(str(e)),400
    

@testcase_blueprint.route('/new',methods = ["POST"])
@jwt_required()
def createTestcases():
    req_data = request.json 
    req_data['project'] = get_project_id(req_data.get("project"))
    req_data['name'] = create_slug(req_data.get("name"))
    user = get_current_user()
    req_data['created_by'] = user.id
    req_data['modified_by'] = user.id
    teststeps = req_data.get('array_of_teststeps')
    del req_data['array_of_teststeps']
    if has_access_to_project(req_data['project'],user.id):
        try:
            data = testcase_schema.load(req_data)
        except ValidationError as err:
            return jsonify(str(err)), 400


        is_exist = TestcaseModel.is_exist(data.get('name'), data.get('project'))

        if is_exist:
            return jsonify({"error": "You already have a testcase of the same name in this project."}), 400

        testcase = TestcaseModel(data)
        testcase.execution_sequence = ""
        for teststep in teststeps:
            testcase.teststeps.append(TestStepModel.query.get(teststep['teststep']))
            testcase.execution_sequence = testcase.execution_sequence + str(teststep.get('teststep')) + ","
            for td in teststep['testdata']:
                testcase.testdatas.append(TestdataModel.query.get(td))
        testcase.save()
        return jsonify({"success" : "testcase created with the given teststeps"}),200
    else:
        return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"}),401

@testcase_blueprint.route('/delete/',methods=["DELETE"])
@jwt_required()
def delete_testcase():
    req_data = request.json
    user = get_current_user()
    try:
        testcase = TestcaseModel.query.get(req_data.get('testcase'))
    except Exception as e:
        return jsonify(str(e)),400
    if testcase:
        if has_access_to_project(testcase.project,user.id):
            testcase.delete()
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make deletions in the project components"}),401
    else:
        return jsonify({"error" : "No such testcase exists"}),404
    return jsonify({"Success" : "testcase deleted successfully"}),200

@testcase_blueprint.route('/update',methods=["PUT"])
@jwt_required()
def update_testcase():
    req_data = request.json
    user = get_current_user()
    try:
        testcase = req_data.get('id')
        testcase = TestcaseModel.query.get(testcase)
        if testcase:
            if has_access_to_project(testcase.project,user.id):
                if req_data.get('name'):
                    name = req_data.get('name')
                    testcase.name = name
                if req_data.get('description'):
                    description = req_data.get('description')
                    testcase.description = description
                if req_data.get('environment'):
                    environment = req_data.get('environment')
                    testcase.environment = environment
                if req_data.get('array_of_teststeps'):
                    teststeps = req_data.get('array_of_teststeps')
                    if len(teststeps) > 0:
                        execution_sequence = ""
                        testcase.teststeps.clear()
                        for i in teststeps:
                            teststep = TestStepModel.query.get(i)
                            execution_sequence = execution_sequence + str(i) + ","
                            testcase.teststeps.append(teststep)
                            testcase.execution_sequence = execution_sequence
                else:
                    return jsonify({"Error" : "You cannot delete all the teststeps, atleast add one to update"}),400
                
                # if req_data.get('array_of_testdata'):
                #     testdatas = req_data.get('array_of_testdatas')
                #     if len(testdatas) > 0:
                #         testcase.testdatas.clear()

                     
                testcase.update({'modified_by' : user.id})
            else:
                return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to make updates in the project components"}),401
        else:
            return jsonify({"error" : "no such endpoint exists"}),404
    except Exception as err:
        return jsonify(str(err)),400
    return jsonify({"Success" : "Testcase Updated Successfully"}),200

