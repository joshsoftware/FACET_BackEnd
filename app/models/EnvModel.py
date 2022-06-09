from datetime import datetime

from marshmallow import Schema, fields
from app.models import db

class EnvModel(db.Model):
    """
    Environment Model
    """

    __tablename__ = 'environments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    url = db.Column(db.String(500), nullable=False)
    project = db.Column(db.Integer, db.ForeignKey('projects.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.url = data.get('url')
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
    def get_all_envs(project_id):
        data = EnvSchema().dump(EnvModel.query.filter_by(project=project_id), many=True)
        return data

    @staticmethod
    def get_one_env(id):
        data = EnvSchema().dump(EnvModel.query.get(id))
        return data

    @staticmethod
    def is_exist(name, project):
        return EnvModel.query.filter_by(name=name, project=project).first() or None

    def __repr__(self):
        return f'<id {self.id}>'
    

class EnvSchema(Schema):
    """
    Environment Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    project = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)