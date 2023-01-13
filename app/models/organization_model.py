"""
Organization module to create and manage the table of organization.
It maintains one to many relationship between organization
and projects respectively using org_projects.
Similarly it maintains the one to many
relationship between organization and users
respectively using org_users.
"""
from datetime import datetime

from marshmallow import fields, Schema

from app.models import db

from app.models.project_model import ProjectSchema

from app.models.user_model import UserSchema


class OrganizationModel(db.Model):
    """
    Organization Model
    """

    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    contact_email_id = db.Column(db.String(50), nullable=False)
    org_projects = db.relationship("ProjectModel", backref="organizations")
    org_users = db.relationship(
        "UserModel",
        backref="organizations",
        primaryjoin="and_(OrganizationModel.id==UserModel.user_organization)",
    )
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get("name")
        self.description = data.get("description")
        self.contact_email_id = data.get("contact_email_id")
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()

    def save(self):
        """
        class function for commiting object into the database
        """
        db.session.add(self)
        db.session.commit()

    def update(self, data=None):
        """
        Class function for updating object changes into the database
        """
        if data:
            for key, item in data.items():
                setattr(self, key, item)
            db.session.commit()

    def delete(self):
        """
        Class function for deleting an object from  the database
        """
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def does_organization_exist(organization_name):
        """
        class method for identifying if an organization exists
        for a given name.
        If the class does not exist, None is sent back
        """
        organization = (
            OrganizationModel.query.filter_by(name=organization_name).first() or None
        )
        return organization

    @staticmethod
    def get_one_organization(organization_id):
        """
        returns details of an organization,
        based on the organization name
        as per the organization schema
        """
        organization = OrganizationSchema(exclude=['org_users']).dump(
            OrganizationModel.query.filter_by(id=organization_id).first()
        )
        return organization

    @staticmethod
    def get_all_organizations():
        """
        returns details of all organizations,
        as per the organization schema
        """
        organizations = OrganizationSchema().dump(
            OrganizationModel.query.all(), many=True
        )
        return organizations

    @staticmethod
    def get_org_projects(organization_id):
        """ "
        returns all the projects associated with
        the organization
        """
        org_projects = []
        org_data = OrganizationModel.query.get(organization_id)
        for project in org_data.org_projects:
            org_projects.append(ProjectSchema().dump(project))
        return org_projects

    @staticmethod
    def get_org_members(organization_id):
        """
        class method which returns all the users
        belonging to the organization
        """
        org_users = []
        org_data = OrganizationModel.query.get(organization_id)
        for user in org_data.org_users:
            org_users.append(UserSchema(exclude=["password"]).dump(user))
        return org_users

    def __repr__(self):
        return f"<id {self.id}>"


class OrganizationSchema(Schema):
    """
    Organization Schema
    """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    contact_email_id = fields.Str(required=True)
    org_users = fields.List(fields.Nested(UserSchema(exclude=["password"])))
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
