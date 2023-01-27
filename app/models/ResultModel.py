from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from marshmallow import Schema, fields
from app.models import db
from app.models.user_model import UserModel

class ResultModel(db.Model):
    """
    Results Model
    """

    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key = True)
    project = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete="CASCADE"))
    result = db.Column(JSON, nullable=False)
    environment = db.Column(JSON, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"))
    executed_on = db.Column(db.DateTime)

    def __init__(self,data):
        self.project = data.get('project')
        self.result = data.get('result')
        self.environment = data.get('environment')
        self.status = data.get('status')
        self.level = data.get('level')
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
        data = ResultSchema().dump(ResultModel.query.filter_by(project=project_id).order_by(ResultModel.id.desc()), many=True)
        for item in data:
            item['executed_by'] = UserModel.get_user_info(item['executed_by'])
        return data
    
    @staticmethod
    def get_one_result(id):
        data = ResultSchema().dump(ResultModel.query.get(id))
        return data

    @staticmethod
    def get_paginated_results(project_id, page_no, row_size):
        try:
            data = ResultModel.query.filter_by(project=project_id).order_by(ResultModel.id.desc()).paginate(page=int(page_no), per_page=int(row_size))
            data = ResultSchema().dump(data.items, many=True)
            for item in data:
                item['executed_by'] = UserModel.get_user_info(item['executed_by'])
            total_results = ResultModel.query.filter_by(project=project_id).count()
            return data, total_results
        except Exception as err:
            return str(err), 0

    @staticmethod
    def is_exist(reportId):
        return ResultModel.query.filter_by(id = reportId).first() or None



class ResultSchema(Schema):
    """
    Results Schema
    """
    id = fields.Int(dump_only=True)
    project = fields.Int(required=True)
    result = fields.Dict(required=True)
    environment = fields.Dict(required=True)
    status = fields.Str(required=True)
    level = fields.Str(required=True)
    executed_by = fields.Int(required=True)
    executed_on = fields.DateTime(dump_only=True)