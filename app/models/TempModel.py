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
    testsuite = db.Column(db.Integer, db.ForeignKey('testsuites.id'))
    testcase = db.Column(db.String(256), nullable=False)
    resp = db.Column(JSON, nullable=False)
    created_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """

        self.testsuite = data.get('testsuite')
        self.testcase = data.get('testcase')
        self.resp = data.get('resp')
        self.created_at = datetime.utcnow()


    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_one(testsuite, testcase):
        data = TempSchema().dump(TempModel.query.filter_by(testsuite=testsuite, testcase=testcase).first())
        return data

    @staticmethod
    def get_all(testsuite):
        data = TempSchema().dump(TempModel.query.get(testsuite=testsuite))
        return data

    @staticmethod
    def get_all_and_delete(testsuite):
        for i in TempModel.query.filter_by(testsuite=testsuite):
            i.delete()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    

class TempSchema(Schema):
    """
    Temp Schema
    """
    id = fields.Int(dump_only=True)
    testsuite = fields.Int(required=True)
    testcase = fields.Str(required=True)
    resp = fields.Dict(required=True)
    created_at = fields.DateTime(dump_only=True)