from datetime import datetime

from marshmallow import Schema, fields
from app.models import db

from app.models.TestcaseModel import TestcaseSchema


testsuite_testcase = db.Table(
    'testsuite_testcase', 
    db.Column('testsuite_id', db.Integer, db.ForeignKey('testsuites.id')),
    db.Column('testcase_id', db.Integer, db.ForeignKey('testcases.id'))
)


class TestsuiteModel(db.Model):
    """
    TestSuite Model
    """

    __tablename__ = 'testsuites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=True)
    project = db.Column(db.Integer, db.ForeignKey('projects.id'))
    environment = db.Column(db.Integer, db.ForeignKey('environments.id'))
    testcases = db.relationship('TestcaseModel', secondary=testsuite_testcase, backref='testcases')
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.description = data.get('description')
        self.project = data.get('project')
        self.environment = data.get('environment')
        self.created_by = data.get('created_by')
        self.created_at = datetime.utcnow()
        self.modified_by = data.get('modified_by')
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
    def get_all_testsuites(project_id):
        data = TestsuiteModel.query.filter_by(project=project_id)
        data = TestsuiteSchema().dump(data, many=True)
        return data

    @staticmethod
    def get_one_testsuite(id):
        data = TestsuiteSchema().dump(TestsuiteModel.query.get(id))
        return data

    @staticmethod
    def is_exist(name, project):
        return TestsuiteModel.query.filter_by(name=name, project=project).first() or None

    def __repr__(self):
        return f'<id {self.id}>'
    

class TestsuiteSchema(Schema):
    """
    Testsuite Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    project = fields.Int(required=True)
    environment = fields.Int(required=True)
    testcases = fields.List(fields.Nested(TestcaseSchema))
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)