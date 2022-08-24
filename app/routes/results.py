from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required
from app.models.ResultModel import ResultModel
from app.models.ProjectModel import ProjectModel
from app.helpers.utils import get_project_id,get_current_user, has_access_to_project

results_blueprint = Blueprint('results', __name__)


@results_blueprint.route('/', methods=["GET"])
@results_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getresults(id=0):
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"))
        if has_access_to_project(project, user.id):
            if id!=0:
                data = ResultModel.get_one_result(id)
                return jsonify(data), 200
            data = ResultModel.get_all_results(project)
            return jsonify({"results": data}), 200
        else:
            return jsonify({"error" : "You do not have access to project,kindly connect with project admin to get access to project components"}),401
    except Exception as e:
        print(e)
        return jsonify(str(e)),400


@results_blueprint.route('/addcomment', methods=['POST'])
@jwt_required()
def add_comment():
    req_data = request.json
    user = get_current_user().id
    try:
        reportId = req_data.get('reportId')
        testcase_name = req_data.get('testcase')
        testdata_name = req_data.get('testdata')
        field_name = req_data.get('field')
        status = req_data.get('status')
        comment = req_data.get('comment')
        report = ResultModel.get_one_result(reportId)
        is_able_to_update = False
        if report and has_access_to_project(report['project'], user):
            newTestcases = report['testcases']
            del report['testcases']

            for testcase in newTestcases:
                if testcase['name']==testcase_name:
                    for testdata in testcase['testdata_combinations']:
                        if testdata['name']==testdata_name:
                            # is_testdata_failed = testdata['status']=="failed"
                            for field in testdata['outcome']:
                                if field['name']==field_name:
                                    field['comment'] = comment
                                    field['status'] = "m" + status
                                    field['updated_by'] = user
                                    is_able_to_update = True

                                    if field['status']=="mpassed":
                                        testdata['no_of_failed_fields'] -= 1
                                        testdata['no_of_passed_fields'] += 1
                                    elif field['status']=="mfailed":
                                        testdata['no_of_failed_fields'] += 1
                                        testdata['no_of_passed_fields'] -= 1

                            if testdata['no_of_failed_fields']==0:
                                testdata['status'] = "passed"
                                testcase['no_of_failed_testdata_combinations'] -= 1
                                testcase['no_of_passed_testdata_combinations'] += 1
                            else:
                                if testdata['status']=="passed":
                                    testdata['status'] = "failed"
                                    testcase['no_of_failed_testdata_combinations'] += 1
                                    testcase['no_of_passed_testdata_combinations'] -= 1
                    if testcase['no_of_failed_testdata_combinations']==0:
                        testcase['status'] = "passed"
                        report['no_of_failed_testcases'] -= 1
                        report['no_of_passed_testcases'] += 1
                    else:
                        if testcase['status']=="passed":
                            testcase['status'] = "failed"
                            report['no_of_failed_testcases'] += 1
                            report['no_of_passed_testcases'] -= 1
            if is_able_to_update:
                updatedResult = ResultModel.query.get(reportId)
                updatedResult.update({
                    "testcases": newTestcases, 
                    "no_of_passed_testcases": report['no_of_passed_testcases'],
                    "no_of_failed_testcases": report['no_of_failed_testcases']
                })
                return jsonify({"message": "Updated Successfully!"}), 200
            return jsonify({"error": "Not Found"}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400


def modify_outcome_ids(data):
    user = get_current_user().id
    for result in data:
        result['project_id'] = ProjectModel.get_one_project(result['project_id'], user).get('name')
    return data
