from datetime import datetime

from marshmallow import Schema, fields
from app.helpers.utils import get_user_name
from app.models import db

from app.models.TestdataModel import TestdataSchema
from app.models.TeststepModel import TeststepSchema


testcase_teststep = db.Table(
    'testcase_teststep', 
    db.Column('testcase_id', db.Integer, db.ForeignKey('testcases.id',ondelete="CASCADE")),
    db.Column('teststep_id', db.Integer, db.ForeignKey('teststeps.id',ondelete="CASCADE"))
)

testcase_testdata = db.Table(
    'testcase_testdata',
    db.Column('testcase_id', db.Integer, db.ForeignKey('testcases.id',ondelete="CASCADE")),
    db.Column('testdata_id', db.Integer, db.ForeignKey('testdata.id',ondelete="CASCADE"))
)

class TestcaseModel(db.Model):
    """
    TestCase Model
    """

    __tablename__ = 'testcases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    project = db.Column(db.Integer, db.ForeignKey('projects.id',ondelete="CASCADE"))
    teststeps = db.relationship('TestStepModel',secondary=testcase_teststep,backref='teststeps')
    testdatas = db.relationship('TestdataModel',secondary=testcase_testdata,backref='testdata')
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
    def get_all_testcases(project_id):
        data = TestcaseModel.query.filter_by(project=project_id)
        data = TestcaseSchema().dump(data, many=True)
        for testcase in data:
            testcase['created_by'] = get_user_name(testcase['created_by'])
            testcase['modified_by'] = get_user_name(testcase['modified_by'])
            arranged_teststeps = TestcaseModel.rearrange_teststeps(testcase['execution_sequence'],testcase)
            testcase['teststeps'] = arranged_teststeps['teststeps']

            selected_testdatas_id = [i['id'] for i in testcase['testdatas']]
            
            for i in testcase['teststeps']:
                i['selected_testdata'] = [testdata['id'] for testdata in i['testdata'] if testdata['id'] in selected_testdatas_id]

            del testcase['testdatas']
        return data

    @staticmethod
    def get_one_testcase(id):
        testcase = TestcaseModel.query.get(id)
        data = TestcaseSchema().dump(testcase)
        # data['teststeps'] = TestsuiteModel.rearrange_teststeps(data['execution_sequence'],data)
        order = testcase.execution_sequence[:-1]
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
        return TestcaseModel.query.filter_by(name=name, project=project).first() or None

    def __repr__(self):
        return f'<id {self.id}>'
    
    def rearrange_teststeps(order,testcase):
        data = {}
        order = testcase.get('execution_sequence')[:-1]
        order = order.split(",")
        teststeps = testcase['teststeps']
        data['teststeps'] = []
        for teststep in order:
            for test in teststeps:
                if int(teststep) == test['id']:
                    data['teststeps'].append(test)
        return data
    

class TestcaseSchema(Schema):
    """
    Testcase Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    project = fields.Int(required=True)
    teststeps = fields.List(fields.Nested(TeststepSchema))
    testdatas = fields.List(fields.Nested(TestdataSchema))
    execution_sequence = fields.Str() 
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)