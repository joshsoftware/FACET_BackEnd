from crypt import methods
from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required
from app.models.ResultModel import ResultModel, ResultSchema
from app.models.ProjectModel import ProjectModel
from app.models.TestcaseModel import TestcaseModel
from app.models.TestsuiteModel import TestsuiteModel
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
            # data = modify_outcome_ids(data)
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
            for testcase in newTestcases['testcases']:
                if testcase['name']==testcase_name:
                    for testdata in testcase['testdata_combinations']:
                        if testdata['name']==testdata_name:
                            for field in testdata['outcome']:
                                if field['name']==field_name:
                                    field['comment'] = comment
                                    field['status'] = status
                                    field['updated_by'] = user
                                    is_able_to_update = True
                                    break
            if is_able_to_update:
                # print(newTestcases)
                updatedResult = ResultModel.query.get(reportId)
                updatedResult.update({"testcases": newTestcases})
                return jsonify({"message": "Updated Successfully!"}), 200
            return jsonify({"error": "Not Found"}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400


# @results_blueprint.route('/update',methods=["PUT"])
# @jwt_required()
# def add_comment():
#     req_data = request.json
#     user = get_current_user()
#     try:
#         result = req_data.get('id')
#         result = ResultModel.query.get(result)
#         if result:
#             if has_access_to_project(result.project_id,user.id):

#                 if req_data.get('comment'):
#                     result.comment = req_data.get('comment')
                
#                 if req_data.get('status'):
#                     result.status = req_data.get('status')
                
#                 result.update()
#             else:
#                 return jsonify({"Error" : "You do not have access to this project,kindly connect with project admin to get make updates in the project component"}),401
#         else:
#             return jsonify({"Error" : "No such result exists"}),404
#     except Exception as err:
#         return jsonify(str(err)),400
#     return jsonify({"Success" : "Result updated successfully"}),200

def modify_outcome_ids(data):
    for result in data:
        result['project_id'] = ProjectModel.get_one_project(result['project_id']).get('name')
    return data
