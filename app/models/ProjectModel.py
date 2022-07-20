from datetime import datetime

from marshmallow import fields, Schema
from app.models import db

from app.models.UserModel import UserSchema

project_member = db.Table(
    'project_member',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('users.id'))
)

class ProjectModel(db.Model):
    """
    Project Model
    """

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    project_admin = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_members = db.relationship('UserModel',secondary = project_member,backref = 'project_members')
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer,db.ForeignKey('users.id'))
    modified_by = db.Column(db.Integer,db.ForeignKey('users.id'))
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.description = data.get('description')
        self.project_admin = data.get('project_admin')
        self.created_at = datetime.utcnow()
        self.created_by = data.get('project_admin')
        self.modified_by = data.get('project_admin')
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
    def get_all_projects(user_id):
        data = ProjectSchema().dump(ProjectModel.query.filter_by(project_admin=user_id), many=True)
        return data

    @staticmethod
    def get_one_project(id):
        data = ProjectSchema().dump(ProjectModel.query.get(id))
        return data

    @staticmethod
    def is_project_exist(name, user):
        return ProjectModel.query.filter_by(name=name, project_admin=user).first()
    
    @staticmethod
    def is_a_member_of_project(id,user_id):
        project = ProjectSchema().dump(ProjectModel.query.get(id))
        members = project['project_members']
        for member in members:
            if member['id'] == user_id:
                return True
        return False


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
    project_members = fields.List(fields.Nested(UserSchema))
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
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