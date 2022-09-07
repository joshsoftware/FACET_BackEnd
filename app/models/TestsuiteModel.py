from datetime import datetime

from marshmallow import Schema, fields
from app.helpers.utils import get_user_name
from app.models import db

from app.models.TeststepModel import TeststepSchema


testsuite_teststep = db.Table(
    'testsuite_teststep', 
    db.Column('testsuite_id', db.Integer, db.ForeignKey('testsuites.id',ondelete="CASCADE")),
    db.Column('teststep_id', db.Integer, db.ForeignKey('teststeps.id',ondelete="CASCADE"))
)


class TestsuiteModel(db.Model):
    """
    TestSuite Model
    """

    __tablename__ = 'testsuites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    project = db.Column(db.Integer, db.ForeignKey('projects.id',ondelete="CASCADE"))
    teststeps = db.relationship('TestStepModel',secondary=testsuite_teststep,backref='teststeps')
    execution_sequence = db.Column(db.String(400))
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="SET NULL"))
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="SET NULL"))
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.description = data.get('description')
        self.project = data.get('project')
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
        for testsuite in data:
            testsuite['created_by'] = get_user_name(testsuite['created_by'])
            testsuite['modified_by'] = get_user_name(testsuite['modified_by'])
            arranged_teststeps = TestsuiteModel.rearrange_teststeps(testsuite['execution_sequence'],testsuite)
            testsuite['teststeps'] = arranged_teststeps['teststeps']
        return data

    @staticmethod
    def get_one_testsuite(id):
        testsuite = TestsuiteModel.query.get(id)
        data = TestsuiteSchema().dump(testsuite)
        # data['teststeps'] = TestsuiteModel.rearrange_teststeps(data['execution_sequence'],data)
        order = testsuite.execution_sequence[:-1]
        teststeps = data['teststeps']
        data['teststeps'] = []
        order = order.split(",")
        for teststep in order:
            for test in teststeps:
                if int(teststep) == test['id']:
                    data['teststeps'].append(test)
        return data

    @staticmethod
    def is_exist(name, project):
        return TestsuiteModel.query.filter_by(name=name, project=project).first() or None

    def __repr__(self):
        return f'<id {self.id}>'
    
    def rearrange_teststeps(order,testsuite):
        data = {}
        order = testsuite.get('execution_sequence')[:-1]
        order = order.split(",")
        teststeps = testsuite['teststeps']
        data['teststeps'] = []
        for teststep in order:
            for test in teststeps:
                if int(teststep) == test['id']:
                    data['teststeps'].append(test)
        return data
    

class TestsuiteSchema(Schema):
    """
    Testsuite Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    project = fields.Int(required=True)
    teststeps = fields.List(fields.Nested(TeststepSchema))
    execution_sequence = fields.Str() 
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)