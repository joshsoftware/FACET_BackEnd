from datetime import datetime
from marshmallow import Schema, fields
from sqlalchemy.dialects.postgresql import JSON
from app.models import db



class TempModel(db.Model):
    """
    Temp Model
    """

    __tablename__ = 'temp'
    id = db.Column(db.Integer, primary_key=True)
    run_time_id = db.Column(db.String(256),nullable=False)
    testcase = db.Column(db.Integer, db.ForeignKey('testcases.id'))
    teststep = db.Column(db.String(256), nullable=False)
    resp = db.Column(JSON, nullable=False)
    created_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """

        self.testcase = data.get('testcase')
        self.teststep = data.get('teststep')
        self.run_time_id = data.get('run_time_id')
        self.resp = data.get('resp')
        self.created_at = datetime.utcnow()


    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_one(testcase, teststeps,run_time_id):
        data = TempSchema().dump(TempModel.query.filter_by(testcase=testcase, teststep=teststeps, run_time_id = run_time_id).first())
        return data

    @staticmethod
    def get_all(testcase, run_time_id):
        data = TempSchema().dump(TempModel.query.get(testcase=testcase, run_time_id=run_time_id))
        return data

    @staticmethod
    def get_all_and_delete(testcase,run_time_id):
        for temp_data in TempModel.query.filter_by(testcase=testcase,run_time_id = run_time_id):
            temp_data.delete()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    

class TempSchema(Schema):
    """
    Temp Schema
    """
    id = fields.Int(dump_only=True)
    testcase = fields.Int(required=True)
    teststep = fields.Str(required=True)
    run_time_id = fields.Str(required=True)
    resp = fields.Dict(required=True)
    created_at = fields.DateTime(dump_only=True)