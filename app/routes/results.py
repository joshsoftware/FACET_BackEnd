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
        if has_access_to_project(project,user.id):
            if id!=0:
                data = ResultModel.get_one_result(id)
                return jsonify(data), 200
            data = ResultModel.get_all_results(project)
            data = modify_outcome_ids(data)
            return jsonify({"results": data}), 200
        else:
            return jsonify({"error" : "You do not have access to project,kindly connect with project admin to get access to project components"}),401
    except Exception as e:
        return jsonify(str(e)),400

@results_blueprint.route('/update',methods=["PUT"])
@jwt_required()
def add_comment():
    req_data = request.json
    user = get_current_user()
    try:
        result = req_data.get('id')
        result = ResultModel.query.get(result)
        if result:
            if has_access_to_project(result.project_id,user.id):

                if req_data.get('comment'):
                    result.comment = req_data.get('comment')
                
                if req_data.get('status'):
                    result.status = req_data.get('status')
                
                result.update()
            else:
                return jsonify({"Error" : "You do not have access to this project,kindly connect with project admin to get make updates in the project component"}),401
        else:
            return jsonify({"Error" : "No such result exists"}),404
    except Exception as err:
        return jsonify(str(err)),400
    return jsonify({"Success" : "Result updated successfully"}),200

def modify_outcome_ids(data):
    for result in data:
        result['project_id'] = ProjectModel.get_one_project(result['project_id']).get('name')
    return data
