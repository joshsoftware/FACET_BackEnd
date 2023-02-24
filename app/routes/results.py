from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.ResultModel import ResultModel
from app.helpers.utils import get_project_id, get_current_user, has_access_to_project
import logging

results_blueprint = Blueprint('results', __name__)


@results_blueprint.route('/', methods=["GET"])
@results_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getresults(id=0):
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"),user.user_organization)
        page_no = request.args.get("page") or 1
        row_size = request.args.get("pageSize") or 20
        logging.info(f"GET request to fetch result by user:{user.id} with params:{dict(request.args)} and url:{request.url}")
        if id != 0:
            data = ResultModel.get_one_result(id)
            logging.info(f"GET request successful, result returned successfully for result id:{id}")
            return jsonify(data), 200

        if not has_access_to_project(project, user.id):
            logging.info(f"GET request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to project,kindly connect with project admin to get access to project components"}), 401

        data, total_results = ResultModel.get_paginated_results(
            project_id=project, page_no=page_no, row_size=row_size)

        if type(data) is str:
            logging.info(f"GET request failed due to the following error:{err}")
            return jsonify({"error": data}), 404
        logging.info(f"GET request successful, results returned successfully for project id:{project}")
        return jsonify({"results": data, "total_results": total_results}), 200

    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@results_blueprint.route('/addcomment', methods=['POST'])
@jwt_required()
def add_comment():
    req_data = request.json
    user = get_current_user()
    logging.info(f"PUT request to update result by user:{user.id} with payload:{req_data}")
    try:
        reportId = req_data.get('reportId')
        teststep_name = req_data.get('teststep')
        testdata_name = req_data.get('testdata')
        field_name = req_data.get('field')
        status = req_data.get('status')
        comment = req_data.get('comment')
        testcase =  req_data.get('testcase') if req_data.get('testcase') else None
        testsuite = req_data.get('testsuite') if req_data.get('testsuite') else None
        project = get_project_id(slug=req_data.get('project'),organization=user.user_organization)
        
        if not has_access_to_project(project, user.id):
            logging.info(f"PUT request failed due to unauthorised access")
            return jsonify({"error": "You do not have access to project,kindly connect with project admin to get access to project components"}), 401

        report = ResultModel.get_one_result(reportId)

        if not report:
            logging.info(f"PUT request failed as no such result exists for the project")
            return jsonify({"error": "result not Found"}), 404

        if testsuite:
            for test_case in report['result']['testsuite_execution']:
                if test_case['testcase']['name'] == testcase:
                    is_able_to_update = teststep_modification(result=test_case,teststep_name=teststep_name,testdata_name=testdata_name,field_name=field_name,status=status,comment=comment, user=user.id)
            updatedResult = ResultModel.query.get(reportId)
            updatedResult.update({
                "result" : report['result']
            })
            return jsonify({"message": "Updated Successfully!"}), 200
        else:
            result = report['result']
            is_able_to_update = teststep_modification(result=result,teststep_name=teststep_name,testdata_name=testdata_name,field_name=field_name,status=status,comment=comment, user=user.id)
            updatedResult = ResultModel.query.get(reportId)
            updatedResult.update({
                "result" : result
            })
        if is_able_to_update:
            logging.info(f"result updated sucessfully")
            return jsonify({"message": "Updated Successfully!"}), 200
    except Exception as err:
        logging.exception(f"PUT request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


def teststep_modification(result,teststep_name,testdata_name,field_name,status,comment,user):
    is_able_to_update = False
    newTeststeps = result['teststeps']
    for teststep in newTeststeps:
        if teststep['name'] == teststep_name:
            for testdata in teststep['testdata_combinations']:
                if testdata['name'] == testdata_name:
                    for field in testdata['outcome']:
                        if field['name'] == field_name:
                            field['comment'] = comment
                            field['status'] = status
                            field['updated_by'] = user
                            field['is_status_manually_updated'] = True
                            is_able_to_update = True

                            if field['status'] == "passed":
                                testdata['no_of_failed_fields'] -= 1
                                testdata['no_of_passed_fields'] += 1
                            elif field['status'] == "failed":
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
                result['no_of_failed_teststeps'] -= 1
                result['no_of_passed_teststeps'] += 1
            else:
                if teststep['status'] == "passed":
                    teststep['status'] = "failed"
                    result['no_of_failed_teststeps'] += 1
                    result['no_of_passed_teststeps'] -= 1
    return is_able_to_update
