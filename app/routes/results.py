from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.ResultModel import ResultModel
from app.models.ProjectModel import ProjectModel
from app.helpers.utils import get_project_id, get_current_user, has_access_to_project

results_blueprint = Blueprint('results', __name__)


@results_blueprint.route('/', methods=["GET"])
@results_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getresults(id=0):
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"))
        page_no = request.args.get("page") or None
        row_size = request.args.get("pageSize") or 20

        if not has_access_to_project(project, user.id):
            return jsonify({"error": "You do not have access to project,kindly connect with project admin to get access to project components"}), 401

        if id != 0:
            data = ResultModel.get_one_result(id)
            return jsonify(data), 200

        data, total_results = ResultModel.get_paginated_results(
            project_id=project, page_no=page_no, row_size=row_size)

        if type(data) is str:
            return jsonify({"error": data}), 404
        return jsonify({"results": data, "total_results": total_results}), 200

    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@results_blueprint.route('/addcomment', methods=['POST'])
@jwt_required()
def add_comment():
    req_data = request.json
    user = get_current_user().id
    try:
        reportId = req_data.get('reportId')
        teststep_name = req_data.get('teststep')
        testdata_name = req_data.get('testdata')
        field_name = req_data.get('field')
        status = req_data.get('status')
        comment = req_data.get('comment')
        report = ResultModel.get_one_result(reportId)
        is_able_to_update = False
        if not report:
            return jsonify({"error": "result not Found"}), 404
        if not has_access_to_project(report['project'], user):
            return jsonify({"error": "You do not have access to project,kindly connect with project admin to get access to project components"}), 401

        newTeststeps = report['teststeps']
        del report['teststeps']

        for teststep in newTeststeps:
            if teststep['name'] == teststep_name:
                for testdata in teststep['testdata_combinations']:
                    if testdata['name'] == testdata_name:
                        # is_testdata_failed = testdata['status']=="failed"
                        for field in testdata['outcome']:
                            if field['name'] == field_name:
                                field['comment'] = comment
                                field['status'] = "m" + status
                                field['updated_by'] = user
                                is_able_to_update = True

                                if field['status'] == "mpassed":
                                    testdata['no_of_failed_fields'] -= 1
                                    testdata['no_of_passed_fields'] += 1
                                elif field['status'] == "mfailed":
                                    testdata['no_of_failed_fields'] += 1
                                    testdata['no_of_passed_fields'] -= 1

                        if testdata['no_of_failed_fields'] == 0:
                            testdata['status'] = "passed"
                            teststep['no_of_failed_testdata_combinations'] -= 1
                            teststep['no_of_passed_testdata_combinations'] += 1
                        else:
                            if testdata['status'] == "passed":
                                testdata['status'] = "failed"
                                teststep['no_of_failed_testdata_combinations'] += 1
                                teststep['no_of_passed_testdata_combinations'] -= 1
                if teststep['no_of_failed_testdata_combinations'] == 0:
                    teststep['status'] = "passed"
                    report['no_of_failed_teststeps'] -= 1
                    report['no_of_passed_teststeps'] += 1
                else:
                    if teststep['status'] == "passed":
                        teststep['status'] = "failed"
                        report['no_of_failed_teststeps'] += 1
                        report['no_of_passed_teststeps'] -= 1
        if is_able_to_update:
            updatedResult = ResultModel.query.get(reportId)
            updatedResult.update({
                "teststeps": newTeststeps,
                "no_of_passed_teststeps": report['no_of_passed_teststeps'],
                "no_of_failed_teststeps": report['no_of_failed_teststeps']
            })
            return jsonify({"message": "Updated Successfully!"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


def modify_outcome_ids(data):
    user = get_current_user().id
    for result in data:
        result['project_id'] = ProjectModel.get_one_project(
            result['project_id'], user).get('name')
    return data
