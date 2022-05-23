from datetime import datetime

from marshmallow import fields, Schema
from app.models import db

class ProjectModel(db.Model):
    """
    Project Model
    """

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.description = data.get('description')
        self.user = data.get('user')
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
    def get_all_projects(user_id):
        return ProjectModel.query.filter_by(user=user_id)

    @staticmethod
    def get_one_project(id):
        return ProjectModel.query.get(id)

    @staticmethod
    def is_project_exist(name, user):
        return ProjectModel.query.filter_by(name=name, user=user).first()

    def __repr__(self):
        return f'<id {self.id}>'
    

class ProjectSchema(Schema):
    """
    Project Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    user = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)