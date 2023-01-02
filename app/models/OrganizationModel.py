from datetime import datetime

from marshmallow import fields, Schema

from app.models.UserModel import UserModel, UserSchema

from app.models import db

class OrganizationModel(db.Model):
    """
    Organization Model
    """

    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    org_super_admin = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="SET NULL"))
    contact_email_id = db.Coumn(db.String(50), nullable=False)
    #org_users = db.relationship('UserModel',secondary = organization_users,backref = 'organizations')
    #org_projects = db.relationship('ProjectModel', secondary = organization_projects, backref='organizations')
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer,db.ForeignKey('users.id',ondelete="SET NULL"))
    modified_by = db.Column(db.Integer,db.ForeignKey('users.id',ondelete="SET NULL"))
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.description = data.get('description')
        self.org_super_admin = data.get('org_super_admin')
        self.contact_email_id = data.get('contact_email_id')
        self.created_at = datetime.utcnow()
        self.created_by = data.get('org_super_admin')
        self.modified_by = data.get('org_super_admin')
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
    
    def __repr__(self):
        return f'<id {self.id}>'

class OrganizationSchema(Schema):
    """
    Organization Schema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    org_super_admin = fields.Int(required=True)
    contact_email_id = fields.Str(required=True)
    #org_users = fields.List(fields.Nested(UserSchema(exclude=['password'])))
    #org_projects = fields.List(fields.Nested(ProjectSchema))
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)
