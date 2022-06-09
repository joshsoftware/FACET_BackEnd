from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from marshmallow import Schema, fields
from app.models import db


class ResultModel(db.Model):
    """
    Results Model
    """

    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    testcase_id = db.Column(db.Integer, db.ForeignKey('testcases.id'), nullable=False)
    testsuite_id = db.Column(db.Integer, db.ForeignKey('testsuites.id'), nullable=False)
    payload_used = db.Column(JSON, nullable = False)
    response = db.Column(JSON,nullable = False)
    comment = db.Column(db.Text,nullable = True)
    created_at = db.Column(db.DateTime)

    def __init__(self,data):
        self.project_id = data.get('project_id')
        self.user = data.get('user')
        self.testcase_id = data.get('testcase_id')
        self.testsuite_id = data.get('testsuite_id')
        self.payload_used = data.get('payload_used')
        self.response = data.get('response')
        self.comment = data.get('comment')
        self.created_at = datetime.utcnow()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, data={}):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.utcnow()
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_results(project_id):
        data = ResultSchema().dump(ResultModel.query.filter_by(project_id=project_id), many=True)
        return data
    
    @staticmethod
    def get_one_result(id):
        data = ResultSchema().dump(ResultModel.query.get(id))
        return data
    
    @staticmethod
    def is_exist(project):
        return ResultModel.query.filter_by(project_id = project).first() or None



class ResultSchema(Schema):
    """
    Results Schema
    """
    id = fields.Int(dump_only=True)
    user = fields.Int(required=True)
    project_id = fields.Int(required=True)
    testcase_id = fields.Int(required=True)
    testsuite_id = fields.Int(required=True)
    payload_used = fields.Dict(required=True)
    response = fields.Dict(required=True)
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)