from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required
from app.models.ResultModel import ResultModel
from app.helpers.utils import get_project_id

results_blueprint = Blueprint('results', __name__)


@results_blueprint.route('/', methods=["GET"])
@results_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getresults(id=0):
    try:
        if id!=0:
            data = ResultModel.get_one_result(id)
            return jsonify(data), 200
        project = get_project_id(request.args.get("project"))
        data = ResultModel.get_all_results(project)
        print(jsonify({"results": data}))
        return jsonify({"results": data}), 200
        
    except Exception as e:
        return jsonify(str(e)),400
