from datetime import datetime

from marshmallow import Schema, fields
from app.models import db
from app.models.ProjectModel import ProjectSchema

from app.models.UserModel import UserSchema

organization_admin = db.Table(
    'organization_admin',
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id')),
    db.Column('admin_id', db.Integer, db.ForeignKey('users.id'))
)

organization_member = db.Table(
    'organization_member',
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('users.id'))
)

class OrganizationModel(db.Model):
    """
    Organization Model
    """
    __tablename__ = "organization"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    admin = db.relationship('UserModel',secondary = organization_admin,backref = 'admin')
    members = db.relationship('UserModel',secondary = organization_member,backref = 'members')
    projects = db.relationship('ProjectModel',back_populates="organization")
    is_private = db.Column(db.Boolean, default = False,nullable = False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self,data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.created_by = data.get('created_by')
        self.is_private = data.get('is_private')
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, data={}):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_all_organizations():
        data = OrganizationModel.query.all()
        data = OrganizationSchema().dump(data,many=True)
        return data
    
    @staticmethod
    def get_one_organization(id):
        data = OrganizationSchema().dump(OrganizationModel.query.get(id))
        return data

    @staticmethod
    def does_organization_exist(name):
        return OrganizationModel.query.filter_by(name=name).first()



class OrganizationSchema(Schema):
    """
    Testsuite Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    admin = fields.List(fields.Nested(UserSchema))
    members = fields.List(fields.Nested(UserSchema))
    projects = fields.Nested(ProjectSchema)
    created_by = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
