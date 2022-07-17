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
    project_admin = db.Column(db.Integer, db.ForeignKey('users.id'))
    members = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"))
    organization = db.relationship("organization", back_populates="projects")
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
        data = ProjectSchema().dump(ProjectModel.query.filter_by(user=user_id), many=True)
        return data

    @staticmethod
    def get_one_project(id):
        data = ProjectSchema().dump(ProjectModel.query.get(id))
        return data

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
    project_admin = fields.Int(required=True)
    members = fields.Int(required=True)
    organization_id = fields.Int(required = False)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
    # id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(50), nullable=False, unique=True)
    # description = db.Column(db.Text, nullable=True)
    # project_admin = db.Column(db.Integer, db.ForeignKey('users.id'))
    # members = db.Column(db.Integer, db.ForeignKey('users.id'))
    # organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"))
    # organization = db.relationship("organization", back_populates="projects")
    # created_at = db.Column(db.DateTime)
    # modified_at = db.Column(db.DateTime)