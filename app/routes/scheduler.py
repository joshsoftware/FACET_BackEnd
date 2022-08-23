from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from app.helpers.utils import get_project_id, has_access_to_project
from app.models.SchedulerModel import SchedulerModel,ScheduleSchema
from app.models.TestsuiteModel import TestsuiteModel
from app.models.EnvModel import EnvModel
from apscheduler.schedulers.background import BackgroundScheduler
from marshmallow import ValidationError
from datetime import datetime
from .scheduler_engine import tests

scheduler_blueprint = Blueprint('scheduler', __name__)
scheduler_schema = ScheduleSchema()
scheduler = BackgroundScheduler({'apscheduler.timezone' : 'Asia/Calcutta'})
scheduler.add_jobstore('sqlalchemy',url='postgresql://poojan:poojan@localhost:5432/scheduler')
scheduler.start()

@scheduler_blueprint.route('/', methods=["GET"])
@scheduler_blueprint.route('/<string:id>', methods=["GET"])
@jwt_required()
def getScheduledJobs(id=0):
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"))
        if has_access_to_project(project,user.id):
            if id!=0:
                data = SchedulerModel.get_one_schedule(id)
                return jsonify(data), 200
            data = SchedulerModel.get_all_schedules(project)
            return jsonify({"scheduled jobs": data}), 200
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to get access to scheduled jobs of the project"}),401
    except Exception as e:
        return jsonify(str(e)),400

@scheduler_blueprint.route('/new',methods=['POST'])
@jwt_required()
def addScheduledJob():
    try:
        req_data = request.json
        req_data['project'] = get_project_id(req_data.get('project'))
        user = get_current_user()
        req_data['scheduled_by'] = user.id
        req_data['start_date_time'] = req_data['startDateTime']
        del req_data['startDateTime']
        if req_data['endDateTime']:
            req_data['end_date_time'] = req_data['endDateTime']
        del req_data['endDateTime']
        req_data['frequency'] = to_frequency(req_data.get('frequency_type'),req_data.get('frequency'))
        if has_access_to_project(req_data.get('project'),user.id):
            try:
                data = scheduler_schema.load(req_data)
            except ValidationError as err:
                return jsonify(str(err)),400
            
            scheduled_job = SchedulerModel(data)
            scheduled_job.save()
            job_data = {'testsuite': scheduled_job.testsuite,'environment' : scheduled_job.environment}
            #trigger type date
            if scheduled_job.frequency_type == 'oneTime':
                job = scheduler.add_job(tests,run_date=str(datetime.fromtimestamp(scheduled_job.start_date_time)),trigger="date",args=[job_data,user.id],id=str(scheduled_job.id))
            #trigger type interval
            elif scheduled_job.frequency_type in ['custom','weekly','daily','bi-weekly']:
                pass
            #trigger type cron job
            elif scheduled_job.frequency_type in ['monthly']:
                pass
            return jsonify({"success": "Job scheduled successfully!"}), 201
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to schedule testsuites of the projects"}),401
    except Exception as e:
        return jsonify(str(e) + "----------"),400

def to_frequency(frequency_type,custom_frequency):
    frequency = {
        "years" : 0,
        "months" : 0,
        "weeks" : 0,
        "days" : 0,
        "hours" : 0,
        "minutes" : 0,
        "seconds" : 0
    }
    if frequency_type == "daily":
        frequency["days"] = 1
    if frequency_type == "weekly":
        frequency["weeks"] = 1
    if frequency_type == "bi-weekly":
        frequency["weeks"] = 2
    if frequency_type == "monthly":
        frequency["months"] = 1
    if frequency_type == "yearly":
        frequency["years"] = 1
    if frequency_type == "custom":
        frequency = custom_frequency
    elif frequency_type == "one-time":
        pass
    return frequency