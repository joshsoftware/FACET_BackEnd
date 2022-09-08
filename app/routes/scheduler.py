import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from app.helpers.utils import get_project_id, has_access_to_project
from app.models.SchedulerModel import SchedulerModel,ScheduleSchema
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app as app
from marshmallow import ValidationError
from datetime import datetime
from .scheduler_engine import tests
from dotenv import load_dotenv
load_dotenv()

scheduler_blueprint = Blueprint('scheduler', __name__)
scheduler_schema = ScheduleSchema()
scheduler = BackgroundScheduler({'apscheduler.timezone' : 'Asia/Calcutta'})
scheduler.add_jobstore('sqlalchemy',url=os.getenv('DATABASE_URL'))
scheduler.start()

def job_monitor():
    
    scheduled_jobs = SchedulerModel.get_all_schedules()
    for job_iterator in range(len(scheduled_jobs)):
        scheduled_jobs[job_iterator] = scheduled_jobs[job_iterator].id
    
    apscheduler_jobs = scheduler.get_jobs()
    for job_iterator in range(len(apscheduler_jobs)):
        apscheduler_jobs[job_iterator] = int(apscheduler_jobs[job_iterator].id)
    
    print("monitoring->AP = ",apscheduler_jobs)
    print("mangaing-> Sch=", scheduled_jobs)

    for job_iterator in scheduled_jobs:
        if job_iterator in apscheduler_jobs:
            continue
        else:
            job = SchedulerModel.query.get(job_iterator)
            job.status = "executed"
            job.save()

monitor_scheduler = BackgroundScheduler({'apscheduler.timezone' : 'Asia/Calcutta'})
monitor_scheduler.start()

monitor_scheduler.add_job(func=job_monitor,trigger="interval",minutes=1)

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
            return jsonify({"scheduled_jobs": data}), 200
        else:
            return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to get access to scheduled jobs of the project"}),401
    except Exception as e:
        return jsonify(str(e)),400

@scheduler_blueprint.route('/new',methods=['POST'])
@jwt_required()
def addScheduledJob():
    with app.app_context():
        try:
            req_data = request.json
            print(req_data)
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
                scheduled_job.status = "to be executed"
                scheduled_job.save()
                
                job_data = {'testcase': scheduled_job.testcase,'environment' : scheduled_job.environment}
                #trigger type date
                if scheduled_job.frequency_type == 'oneTime':
                    job = scheduler.add_job(tests,run_date=str(datetime.fromtimestamp(scheduled_job.start_date_time)),trigger="date",args=[job_data,user.id],id=str(scheduled_job.id))
                #trigger type interval
                else:
                    if scheduled_job.end_date_time:
                        job = scheduler.add_job(tests,start_date=str(datetime.fromtimestamp(scheduled_job.start_date_time)),end_date=str(datetime.fromtimestamp(scheduled_job.end_date_time)),trigger="interval",args=[job_data,user.id],id=str(scheduled_job.id),seconds=scheduled_job.frequency['seconds'],minutes=scheduled_job.frequency['minutes'],hours=scheduled_job.frequency['hours'],days=scheduled_job.frequency['days'],weeks=scheduled_job.frequency['weeks'])
                    else:
                        job = scheduler.add_job(tests,start_date=str(datetime.fromtimestamp(scheduled_job.start_date_time)),trigger="interval",args=[job_data,user.id],id=str(scheduled_job.id),seconds=scheduled_job.frequency['seconds'],minutes=scheduled_job.frequency['minutes'],hours=scheduled_job.frequency['hours'],days=scheduled_job.frequency['days'],weeks=scheduled_job.frequency['weeks'])
                return jsonify({"success": "Job scheduled successfully!"}), 201
            else:
                return jsonify({"Error" : "You do not have access to this project, kindly connect to project admin to schedule testcases of the projects"}),401
        except Exception as e:
            return jsonify(str(e) + "----------"),400

@scheduler_blueprint.route('/Pause_a_job',methods=["PUT"])
def pause_a_job():
    try:
        data = request.json
        job_id = data.get('id')
        pauser = scheduler.pause_job(job_id=job_id)
        scheduled_job = SchedulerModel.query.get(job_id)
        scheduled_job.status = "paused"
        scheduled_job.save()
        return jsonify({"Success" : "Job paused successfully"}),200
    except Exception as err:
        return jsonify(str(err)),400

@scheduler_blueprint.route('/Resume_a_job',methods=["PUT"])
def resume_a_job():
    try:
        data = request.json
        job_id = data.get('id')
        hit_resume = scheduler.resume_job(job_id=job_id)
        scheduled_job = SchedulerModel.query.get(job_id)
        scheduled_job.status = "on-going"
        scheduled_job.save()
        return jsonify({"Success" : "Job resumed successfully"}),200
    except Exception as err:
        return jsonify(str(err)),400

@scheduler_blueprint.route('/delete/',methods=["DELETE"])
def delete_a_job():
    try:
        data = request.json
        job_id = data.get('id')
        remover = scheduler.remove_job(job_id=job_id)
        scheduled_job = SchedulerModel.query.get(job_id)
        scheduled_job.delete()
        return jsonify({"Success" : "Job removed successfully"}),200
    except Exception as err:
        return jsonify(str(err)),400

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
        frequency["weeks"] = 4
    if frequency_type == "yearly":
        frequency["weeks"] = 52
    if frequency_type == "custom":
        frequency = custom_frequency
    elif frequency_type == "one-time":
        pass
    return frequency
