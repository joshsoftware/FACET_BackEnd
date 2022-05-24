from datetime import datetime

from marshmallow import Schema, fields
from app.models import db
from app.models.TestdataModel import TestdataSchema

class TestcaseModel(db.Model):
    """
    Testcase Model
    """

    __tablename__ = 'testcases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    endponit = db.Column(db.Integer, db.ForeignKey('endpoints.id'), nullable=False)
    header = db.Column(db.Integer, db.ForeignKey('headers.id'), nullable=False)
    payload = db.Column(db.Integer, db.ForeignKey('payloads.id'), nullable=False)
    project = db.Column(db.Integer, db.ForeignKey('projects.id'))
    testdata = db.relationship('TestdataModel', backref='testcases', lazy=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.endpoint = data.get('endpoint')
        self.header = data.get('header')
        self.payload = data.get('payload')
        self.project = data.get('project')
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_testcases(project_id):
        data = TestcaseSchema().dump(TestcaseModel.query.filter_by(project=project_id), many=True)
        return data

    @staticmethod
    def get_one_testcase(id):
        data = TestcaseSchema().dump(TestcaseModel.query.get(id))
        return data

    def __repr__(self):
        return f'<id {self.id}>'
    

class TestcaseSchema(Schema):
    """
    Testcase Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    endpoint = fields.Int(required=True)
    header = fields.Int(required=True)
    payload = fields.Int(required=True)
    project = fields.Int(required=True)
    testdata = fields.Nested(TestdataSchema)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)