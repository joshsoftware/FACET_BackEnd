from datetime import datetime

from marshmallow import Schema, fields
from sqlalchemy.dialects.postgresql import JSON
from app.helpers.utils import get_user_name
from app.models import db

class TestdataModel(db.Model):
    """
    Testdata Model
    """

    __tablename__ = 'testdata'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    payload = db.Column(JSON, nullable=False)
    parameters = db.Column(JSON, default={})
    expected_outcome = db.Column(JSON, nullable=False)
    testcase = db.Column(db.Integer, db.ForeignKey('testcases.id',ondelete="CASCADE"))
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="SET NULL"))
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="SET NULL"))
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.payload = data.get('payload')
        self.parameters = data.get('parameters')
        self.expected_outcome = data.get('expected_outcome')
        self.testcase = data.get('testcase')
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
    def get_all_testdatas(testcase_id):
        data = TestdataSchema().dump(TestdataModel.query.filter_by(testcase=testcase_id), many=True)
        for testdata in data:
            testdata['created_by'] = get_user_name(testdata['created_by'])
            testdata['modified_by'] = get_user_name(testdata['modified_by'])
        return data

    @staticmethod
    def get_one_testdata(id):
        data = TestdataSchema().dump(TestdataModel.query.get(id))
        return data

    @staticmethod
    def is_exist(name, testcase):
        return TestdataModel.query.filter_by(name=name, testcase=testcase).first() or None

    def __repr__(self):
        return f'<id {self.id}>'
    

class TestdataSchema(Schema):
    """
    Testdata Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    payload = fields.Dict(required=True)
    parameters = fields.Dict(required=True)
    expected_outcome = fields.List(fields.Dict(), required=True)
    testcase = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)   