from sqlalchemy.dialects.postgresql import JSON
from app.models import db
from marshmallow import Schema, fields
from datetime import datetime

from app.models.user_model import UserModel
from app.models.TestsuiteModel import TestsuiteModel
from app.models.TestcaseModel import TestcaseModel
from app.models.EnvModel import EnvModel


class SchedulerModel(db.Model):
    """
    Schedule Model
    """

    __tablename__ = "scheduler"
    id = db.Column(db.Integer, primary_key=True)
    scheduled_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"))
    project = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete="CASCADE"))
    testsuite = db.Column(db.Integer, db.ForeignKey('testsuites.id', ondelete="CASCADE"))
    testcase = db.Column(db.Integer, db.ForeignKey('testcases.id', ondelete="CASCADE"))
    environment = db.Column(db.Integer, db.ForeignKey('environments.id', ondelete="CASCADE"))
    level = db.Column(db.String(100), nullable=False)
    frequency_type = db.Column(db.String(100), nullable=False)
    frequency = db.Column(JSON, nullable=False)
    start_date_time = db.Column(db.Float, nullable=False)
    end_date_time = db.Column(db.Float)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime)

    def __init__(self,data):
        self.scheduled_by = data.get('scheduled_by')
        self.project = data.get('project')
        self.testsuite = data.get('testsuite')
        self.testcase = data.get('testcase')
        self.environment = data.get('environment')
        self.level = data.get('level')
        self.frequency_type = data.get('frequency_type')
        self.frequency = data.get('frequency')
        self.start_date_time = data.get('start_date_time')
        self.end_date_time = data.get('end_date_time')
        self.status = data.get('status')
        self.created_at = datetime.utcnow()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, data={}):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # @staticmethod
    # def is_exist(testcase,environment):
    #     return SchedulerModel.query.filter_by(testcase_id = testcase,environment_id = environment) or None
    
    @staticmethod
    def get_one_schedule(id):
        data = ScheduleSchema().dump(SchedulerModel.query.get(id))
        return data
    
    @staticmethod
    def get_all_schedules(project_id = None):
        if project_id:
            data = ScheduleSchema().dump(SchedulerModel.query.filter_by(project=project_id).order_by(SchedulerModel.id.desc()), many=True)
            for job in data:
                job['start_date_time'] = datetime.fromtimestamp(job['start_date_time'])
                job['scheduled_by'] = UserModel.get_user_name(job['scheduled_by'])
                if job.get('testcase') is not None:
                    job['testcase'] = TestcaseModel.get_one_testcase(job['testcase']).get('name')
                else:
                    job['testsuite'] = TestsuiteModel.get_one_testsuite(job['testsuite']).get('name')
                job['environment'] = EnvModel.get_one_env(job['environment']).get('name')
                if job['end_date_time']:
                    job['end_date_time'] = datetime.fromtimestamp(job['end_date_time'])
        else:
            data = SchedulerModel.query.all()
        return data
    
    @staticmethod
    def get_all_non_executed_scheduled_jobs():
        return [job.__dict__ for job in SchedulerModel.query.filter_by(status="ongoing")]


class ScheduleSchema(Schema):
    """
    Schedule Schema
    """
    id = fields.Int(dump_only=True)
    scheduled_by = fields.Int(required=True)
    project = fields.Int(required=True)
    testcase = fields.Int()
    testsuite = fields.Int()
    environment = fields.Int(required=True)
    level = fields.Str(required=True)
    frequency_type = fields.Str(required=True)
    frequency = fields.Dict(required=True)
    start_date_time = fields.Float(required=True)
    end_date_time = fields.Float()
    status = fields.Str()
    created_at = fields.DateTime(dump_ony=True)
 
        