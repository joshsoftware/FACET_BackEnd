from datetime import datetime

from marshmallow import Schema, fields
from app.helpers.utils import get_user_name
from app.models import db
from sqlalchemy.dialects.postgresql import JSON

class HeaderModel(db.Model):
    """
    Header Model
    """

    __tablename__ = 'headers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    header = db.Column(JSON, nullable=False)
    project = db.Column(db.Integer, db.ForeignKey('projects.id',ondelete="CASCADE"))
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.header = data.get('header')
        self.project = data.get('project')
        self.created_at = datetime.utcnow()
        self.created_by = data.get('created_by')
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
    def get_all_headers(project_id):
        data = HeaderSchema().dump(HeaderModel.query.filter_by(project=project_id), many=True)
        for header in data:
            header['created_by'] = get_user_name(header['created_by'])
            header['modified_by'] = get_user_name(header['modified_by'])
        return data

    @staticmethod
    def get_one_header(id):
        data = HeaderSchema().dump(HeaderModel.query.get(id))
        return data

    @staticmethod
    def is_exist(name, project):
        return HeaderModel.query.filter_by(name=name, project=project).first() or None

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
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)