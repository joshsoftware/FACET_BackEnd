from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from marshmallow import Schema, fields
from app.models import db
from app.models.UserModel import UserModel, UserSchema


class ResultModel(db.Model):
    """
    Results Model
    """

    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key = True)
    project = db.Column(db.Integer, db.ForeignKey('projects.id',ondelete="CASCADE"))
    testsuite = db.Column(JSON, nullable=False)
    testcases = db.Column(JSON, nullable=False)
    environment = db.Column(JSON, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    no_of_passed_testcases = db.Column(db.Integer)
    no_of_failed_testcases = db.Column(db.Integer)
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"))
    executed_on = db.Column(db.DateTime)

    def __init__(self,data):
        self.project = data.get('project')
        self.testsuite = data.get('testsuite')
        self.testcases = data.get('testcases')
        self.environment = data.get('environment')
        self.status = data.get('status')
        self.no_of_passed_testcases = data.get('no_of_passed_testcases')
        self.no_of_failed_testcases = data.get('no_of_failed_testcases')
        self.executed_by = data.get('executed_by')
        self.executed_on = datetime.utcnow()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, data={}):
        for key, item in data.items():
            setattr(self, key, item)
        # self.modified_at = datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_results(project_id):
        data = ResultSchema().dump(ResultModel.query.filter_by(project=project_id), many=True)
        for item in data:
            item['executed_by'] = UserModel.get_user_info(item['executed_by'])
        return data
    
    @staticmethod
    def get_one_result(id):
        data = ResultSchema().dump(ResultModel.query.get(id))
        return data
    
    @staticmethod
    def is_exist(reportId):
        return ResultModel.query.filter_by(id = reportId).first() or None



class ResultSchema(Schema):
    """
    Results Schema
    """
    id = fields.Int(dump_only=True)
    project = fields.Int(required=True)
    testsuite = fields.Dict(required=True)
    testcases = fields.List(fields.Dict(), required=True)
    environment = fields.Dict(required=True)
    status = fields.Str(required=True)
    no_of_passed_testcases = fields.Int(required=True)
    no_of_failed_testcases = fields.Int(required=True)
    executed_by = fields.Int(required=True)
    executed_on = fields.DateTime(dump_only=True)