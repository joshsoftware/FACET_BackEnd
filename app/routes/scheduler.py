import os
import pytz
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from app.helpers.utils import get_project_id, has_access_to_project
from app.models.SchedulerModel import SchedulerModel, ScheduleSchema
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app as app
from marshmallow import ValidationError
from datetime import datetime
from .engine import scheduler_engine
from dotenv import load_dotenv
import logging

load_dotenv()

scheduler_blueprint = Blueprint("scheduler", __name__)
scheduler_schema = ScheduleSchema()
scheduler = BackgroundScheduler({"apscheduler.timezone": "Asia/Calcutta"})
scheduler.add_jobstore("sqlalchemy", url=os.getenv("DATABASE_URL"))
scheduler.start()

ist_tz = pytz.timezone("Asia/Kolkata")


def job_monitor():
    scheduled_jobs = SchedulerModel.get_all_non_executed_scheduled_jobs()
    for job_iterator in range(len(scheduled_jobs)):
        scheduled_jobs[job_iterator] = scheduled_jobs[job_iterator]["id"]

    apscheduler_jobs = scheduler.get_jobs()
    for job_iterator in range(len(apscheduler_jobs)):
        apscheduler_jobs[job_iterator] = int(apscheduler_jobs[job_iterator].id)

    print("to be monitored", scheduled_jobs)
    print("monitoring", apscheduler_jobs)
    for job_iterator in scheduled_jobs:
        if job_iterator in apscheduler_jobs:
            continue
        else:
            job = SchedulerModel.query.get(job_iterator)
            job.status = "executed"
            job.save()


monitor_scheduler = BackgroundScheduler({"apscheduler.timezone": "Asia/Calcutta"})
monitor_scheduler.start()

monitor_scheduler.add_job(func=job_monitor, trigger="interval", seconds=10)


@scheduler_blueprint.route("", methods=["GET"])
@scheduler_blueprint.route("/<string:id>", methods=["GET"])
@jwt_required()
def getScheduledJobs(id=0):
    try:
        user = get_current_user()
        project = get_project_id(request.args.get("project"), user.user_organization)
        logging.info(
            f"GET request to fetch scheduled jobs by user:{user.id} with params:{dict(request.args)} and url:{request.url}"
        )
        if not has_access_to_project(project, user.id):
            logging.info(f"GET request failed due to unauthorised access")
            return (
                jsonify(
                    {
                        "Error": "You do not have access to this project, kindly connect to project admin to get access to scheduled jobs of the project"
                    }
                ),
                401,
            )
        if id != 0:
            data = SchedulerModel.get_one_schedule(id)
            logging.info(
                f"GET request successful, scheduled jobs returned successfully for scheduled jobs id:{id}"
            )
            return jsonify(data), 200
        data = SchedulerModel.get_all_schedules(project)
        logging.info(
            f"GET request successful, scheduled jobs returned successfully for project id:{project}"
        )
        return jsonify({"scheduled_jobs": data}), 200
    except Exception as err:
        logging.exception(f"GET request failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400


@scheduler_blueprint.route("", methods=["POST"])
@jwt_required()
def addScheduledJob():
    """
    POST request route to create scheduled executions
    Requires:
        -project : project_name
        -level : string in -> ["testsuite","testcase"]
        -testsuite : id (optional)
        -testcase : id (optional)
        -frequency_type: string from -> ["oneTime","interval"]
        -frequency : {"years": 0,"months": 0,"weeks": 0,"days": 0,"hours": 0,"minutes": 0,"seconds": 0}
        -startDateTime : Epoch time value (necessary)
        -endDateTime : Epoch time value (optional)
        Note either testsuite or testcase must be provided and should match the string in level.
    Response:
        - message: job scheduled successfully with status code 200
        - Error message "something went wrong" with status code 400 if anything goes wrong due to data inconsistency or server issue.
        - Error message "invalid payload provided, level does not match the sent execution field" with status code 400 due to faulty payload
        - Error message of unauthorized access with status code 401 if the user does not have access
    """
    with app.app_context():
        try:
            user = get_current_user()
            req_data = request.json
            req_data["project"] = get_project_id(
                req_data.get("project"), user.user_organization
            )
            logging.info(
                f"POST request to create a scheduled job by user:{user.id} with payload:{req_data}"
            )
            req_data["scheduled_by"] = user.id
            req_data["start_date_time"] = req_data["startDateTime"]
            del req_data["startDateTime"]
            if req_data["endDateTime"]:
                req_data["end_date_time"] = req_data["endDateTime"]
            del req_data["endDateTime"]
            req_data["frequency"] = to_frequency(
                req_data.get("frequency_type"), req_data.get("frequency")
            )

            if not has_access_to_project(req_data.get("project"), user.id):
                logging.info(f"POST request failed due to unauthorised access")
                return (
                    jsonify(
                        {
                            "error": "You do not have access to project,kindly connect with project admin to get access to project components"
                        }
                    ),
                    401,
                )

            is_req_data_valid = (
                req_data.get("testsuite") and req_data["level"] == "testsuite"
            ) or (req_data.get("testcase") and req_data["level"] == "testcase")

            if not is_req_data_valid:
                return (
                    jsonify(
                        {
                            "error": "invalid payload provided, level does not match the sent execution field"
                        }
                    ),
                    400,
                )

            try:
                data = scheduler_schema.load(req_data)
            except ValidationError as err:
                logging.error(
                    f"POST request to create a scheduled job failed due to the following error:{err}"
                )
                return jsonify({"error": str(err)}), 400

            scheduled_job = SchedulerModel(data)
            scheduled_job.status = "to be executed"
            scheduled_job.save()

            execution_start_time = datetime.utcfromtimestamp(
                scheduled_job.start_date_time
            )
            execution_start_time = execution_start_time.replace(
                tzinfo=pytz.utc
            ).astimezone(ist_tz)

            job_data = {"environment": scheduled_job.environment}
            if req_data["level"] == "testcase":
                job_data["testcase"] = scheduled_job.testcase
            else:
                job_data["testsuite"] = scheduled_job.testsuite
            # trigger type date
            if scheduled_job.frequency_type == "oneTime":
                job = scheduler.add_job(
                    scheduler_engine,
                    run_date=str(execution_start_time),
                    trigger="date",
                    args=[job_data, user.id],
                    id=str(scheduled_job.id),
                )
            # trigger type interval
            else:
                if scheduled_job.end_date_time:
                    execution_end_time = datetime.utcfromtimestamp(
                        scheduled_job.end_date_time
                    )
                    execution_end_time = execution_end_time.replace(
                        tzinfo=pytz.utc
                    ).astimezone(ist_tz)
                    job = scheduler.add_job(
                        scheduler_engine,
                        start_date=str(execution_start_time),
                        end_date=str(execution_end_time),
                        trigger="interval",
                        args=[job_data, user.id],
                        id=str(scheduled_job.id),
                        seconds=scheduled_job.frequency["seconds"],
                        minutes=scheduled_job.frequency["minutes"],
                        hours=scheduled_job.frequency["hours"],
                        days=scheduled_job.frequency["days"],
                        weeks=scheduled_job.frequency["weeks"],
                    )
                else:
                    job = scheduler.add_job(
                        scheduler_engine,
                        start_date=str(execution_start_time),
                        trigger="interval",
                        args=[job_data, user.id],
                        id=str(scheduled_job.id),
                        seconds=scheduled_job.frequency["seconds"],
                        minutes=scheduled_job.frequency["minutes"],
                        hours=scheduled_job.frequency["hours"],
                        days=scheduled_job.frequency["days"],
                        weeks=scheduled_job.frequency["weeks"],
                    )
            logging.info(f"job scheduled successfully")
            return jsonify({"message": "Job scheduled successfully!"}), 201

        except Exception as err:
            logging.exception(f"POST request failed due to the following error:{err}")
            return jsonify({"error": "something went wrong"}), 400


@scheduler_blueprint.route("/Pause_a_job", methods=["PUT"])
def pause_a_job():
    try:
        data = request.json
        job_id = data.get("id")
        pauser = scheduler.pause_job(job_id=job_id)
        scheduled_job = SchedulerModel.query.get(job_id)
        scheduled_job.status = "paused"
        scheduled_job.save()
        return jsonify({"message": "Job paused successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@scheduler_blueprint.route("/Resume_a_job", methods=["PUT"])
def resume_a_job():
    try:
        data = request.json
        job_id = data.get("id")
        hit_resume = scheduler.resume_job(job_id=job_id)
        scheduled_job = SchedulerModel.query.get(job_id)
        scheduled_job.status = "on-going"
        scheduled_job.save()
        return jsonify({"message": "Job resumed successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


@scheduler_blueprint.route("/delete/", methods=["DELETE"])
def delete_a_job():
    try:
        data = request.json
        job_id = data.get("id")
        remover = scheduler.remove_job(job_id=job_id)
        scheduled_job = SchedulerModel.query.get(job_id)
        scheduled_job.delete()
        return jsonify({"message": "Job removed successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({"error": "something went wrong"}), 400


def to_frequency(frequency_type, custom_frequency):
    frequency = {
        "years": 0,
        "months": 0,
        "weeks": 0,
        "days": 0,
        "hours": 0,
        "minutes": 0,
        "seconds": 0,
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
