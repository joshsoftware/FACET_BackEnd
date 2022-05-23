from datetime import datetime

from marshmallow import Schema, fields
from app.models import db
from sqlalchemy.dialects.postgresql import JSON

class HeaderModel(db.Model):
    """
    Header Model
    """

    __tablename__ = 'headers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    header = db.Column(JSON, nullable=False)
    project = db.Column(db.Integer, db.ForeignKey('projects.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.header = data.get('header')
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
    def get_all_headers(project_id):
        return HeaderModel.query.filter_by(project=project_id)

    @staticmethod
    def get_one_header(id):
        return HeaderModel.query.get(id)

    def __repr__(self):
        return f'<id {self.id}>'
    

class HeaderSchema(Schema):
    """
    Header Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    header = fields.Dict(required=True)
    project = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)