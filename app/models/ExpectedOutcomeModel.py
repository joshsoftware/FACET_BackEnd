from datetime import datetime
from marshmallow import Schema, fields
from sqlalchemy.dialects.postgresql import JSON
from app.helpers.utils import get_user_name
from app.models import db

class ExpectedOutcomeModel(db.Model):
    '''
    Expected_Outcome Model
    '''
    __tablename__ = 'expected_outcome'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    payload = db.Column(db.Integer,db.ForeignKey('payloads.id',ondelete="CASCADE"))
    expected_outcome = db.Column(JSON, nullable=False)
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="SET NULL"))
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="SET NULL"))
    modified_at = db.Column(db.DateTime)

    def __init__(self,data):
        self.name = data.get('name')
        self.payload = data.get('payload')
        self.expected_outcome = data.get('expected_outcome')
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
    def get_all_expected_outcomes(payload_id):
        data = ExpectedOutcomeSchema().dump(ExpectedOutcomeModel.query.filter_by(payload=payload_id), many=True)
        for expected_outcome in data:
            expected_outcome['created_by'] = get_user_name(expected_outcome['created_by'])
            expected_outcome['modified_by'] = get_user_name(expected_outcome['modified_by'])
        return data

    @staticmethod
    def get_one_expected_outcome(id):
        data = ExpectedOutcomeSchema().dump(ExpectedOutcomeModel.query.get(id))
        return data

    @staticmethod
    def is_exist(name, payload_id):
        return ExpectedOutcomeModel.query.filter_by(name=name,payload=payload_id).first() or None

    def __repr__(self):
        return f'<id {self.id}>'


class ExpectedOutcomeSchema(Schema):
    """
    Expected Outcome Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    payload = fields.Int(required=True)
    expected_outcome = fields.List(fields.Dict(), required=True)
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)