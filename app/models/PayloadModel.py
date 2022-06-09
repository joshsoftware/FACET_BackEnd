from datetime import datetime

from marshmallow import Schema, fields
from sqlalchemy.dialects.postgresql import JSON
from app.models import db

class PayloadModel(db.Model):
    """
    Payload Model
    """

    __tablename__ = 'payloads'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    payload = db.Column(JSON, nullable=False)
    expected_outcome = db.Column(JSON, nullable=False)
    project = db.Column(db.Integer, db.ForeignKey('projects.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.payload = data.get('payload')
        self.expected_outcome = data.get('expected_outcome')
        self.project = data.get('project')
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
    def get_all_payloads(project_id):
        data = PayloadSchema().dump(PayloadModel.query.filter_by(project=project_id), many=True)
        return data

    @staticmethod
    def get_one_payload(id):
        data = PayloadSchema().dump(PayloadModel.query.get(id))
        return data

    @staticmethod
    def is_exist(name, project):
        return PayloadModel.query.filter_by(name=name, project=project).first() or None

    def __repr__(self):
        return f'<id {self.id}>'
    

class PayloadSchema(Schema):
    """
    Payload Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    payload = fields.Dict(required=True)
    expected_outcome = fields.Dict(required=True)
    project = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)