"""
Organization module to create and manage the table of organization,
using an association table for many to many
relationship of organization and projects.
It also uses OrganizationUser Class for capturing many to many
relationship between user and organization,
while maitaining the privilege level for each user.
"""
from datetime import datetime

from marshmallow import fields, Schema

from app.models import db

organization_projects = db.Table(
    "organization_projects",
    db.Model.metadata,
    db.Column(
        "organization_id",
        db.Integer,
        db.ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "project_id",
        db.Integer,
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class OrganizationModel(db.Model):
    """
    Organization Model
    """

    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    org_super_admin = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    contact_email_id = db.Column(db.String(50), nullable=False)
    org_projects = db.relationship(
        "ProjectModel", secondary=organization_projects, backref="organizations"
    )
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    modified_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get("name")
        self.description = data.get("description")
        self.org_super_admin = data.get("org_super_admin")
        self.contact_email_id = data.get("contact_email_id")
        self.created_at = datetime.utcnow()
        self.created_by = data.get("org_super_admin")
        self.modified_by = data.get("org_super_admin")
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
        organization = OrganizationModel.query.filter_by(name=organization_name).first()
        return organization

    @staticmethod
    def get_one_organization(organization_name):
        """
        returns details of an organization,
        based on the organization name
        as per the organization schema
        """
        organization = OrganizationSchema().dump(
            OrganizationModel.query.filter_by(name=organization_name).first()
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

    def __repr__(self):
        return f"<id {self.id}>"


class OrganizationSchema(Schema):
    """
    Organization Schema
    """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    org_super_admin = fields.Int(required=True)
    contact_email_id = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)
