from datetime import datetime

from marshmallow import Schema, fields
from app.models import db

class EndpointModel(db.Model):
    """
    Endpoint Model
    """

    __tablename__ = 'endpoints'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    endponit = db.Column(db.String(500), nullable=False)
    project = db.Column(db.Integer, db.ForeignKey('projects.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.endpoint = data.get('endpoint')
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
    def get_all_endpoints(project_id):
        return EndpointModel.query.filter_by(project=project_id)

    @staticmethod
    def get_one_endpoint(id):
        return EndpointModel.query.get(id)

    def __repr__(self):
        return f'<id {self.id}>'
    

class EndpointSchema(Schema):
    """
    Endpoint Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    endpoint = fields.Str(required=True)
    project = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)