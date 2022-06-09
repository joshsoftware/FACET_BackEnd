from datetime import datetime

from marshmallow import Schema, fields
from app.models import db
from app.models.TestdataModel import TestdataSchema
from app.models.EndpointModel import EndpointSchema
from app.models.HeaderModel import HeaderSchema
from app.models.PayloadModel import PayloadSchema
from app.models.ProjectModel import ProjectSchema


class TestcaseModel(db.Model):
    """
    Testcase Model
    """

    __tablename__ = 'testcases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('endpoints.id'), nullable=False)
    method = db.Column(db.String, nullable=False)
    header_id = db.Column(db.Integer, db.ForeignKey('headers.id'), nullable=False)
    payload_id = db.Column(db.Integer, db.ForeignKey('payloads.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    endpoint = db.relationship('EndpointModel', foreign_keys=endpoint_id)
    header = db.relationship('HeaderModel', foreign_keys=header_id)
    payload = db.relationship('PayloadModel', foreign_keys=payload_id)
    project = db.relationship('ProjectModel', foreign_keys=project_id)
    testdata = db.relationship('TestdataModel', backref='testcases', lazy=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.endpoint_id = data.get('endpoint_id')
        self.method = data.get('method')
        self.header_id = data.get('header_id')
        self.payload_id = data.get('payload_id')
        self.project_id = data.get('project_id')
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, data = {}):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_testcases(project_id):
        data = TestcaseSchema().dump(TestcaseModel.query.filter_by(project_id=project_id), many=True)
        return data

    @staticmethod
    def get_one_testcase(id):
        data = TestcaseSchema().dump(TestcaseModel.query.get(id))
        return data
    
    @staticmethod
    def is_exist(name, project):
        return TestcaseModel.query.filter_by(name=name, project_id=project).first() or None

    def __repr__(self):
        return f'<id {self.id}>'
    

class TestcaseSchema(Schema):
    """
    Testcase Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    endpoint_id = fields.Int(required=True)
    method = fields.Str(required=True)
    header_id = fields.Int(required=True)
    payload_id = fields.Int(required=True)
    project_id = fields.Int(required=True)
    endpoint = fields.Nested(EndpointSchema)
    header = fields.Nested(HeaderSchema)
    payload = fields.Nested(PayloadSchema)
    project = fields.Nested(ProjectSchema)
    testdata = fields.List(fields.Nested(TestdataSchema))
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)