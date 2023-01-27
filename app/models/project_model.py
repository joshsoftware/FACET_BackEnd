"""
Project module to create and manage the table of projects,
using an association table for many to many
relationship of project and users.
It also contains Project Schema using Marshmallow
for validation and conversion of object data into
human readable json format.
The project model also maintains a One to many relationship
between organization and projects respectivelty using the
project_organization field, which stores the organization id
the project is associated to.
"""
from datetime import datetime

from marshmallow import fields, Schema

from app.models.user_model import UserModel, UserSchema

from app.models import db

project_member = db.Table(
    "project_member",
    db.Model.metadata,
    db.Column(
        "project_id",
        db.Integer,
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "member_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ProjectModel(db.Model):
    """
    Project Model
    """

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    project_admin = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    project_members = db.relationship(
        "UserModel", secondary=project_member, backref="projects"
    )
    project_organization = db.Column(
        db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE")
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
        self.project_admin = data.get("project_admin")
        self.project_organization = data.get('project_organization')
        self.created_at = datetime.utcnow()
        self.created_by = data.get("project_admin")
        self.modified_by = data.get("project_admin")
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
    def get_all_projects(user_id):
        """
        Class method for fetching all the projects
        to which the user is associated to,
        either as owner or as member
        """
        data = ProjectSchema().dump(
            db.session.query(ProjectModel)
            .join(project_member)
            .where(project_member.c.member_id == user_id),
            many=True,
        )
        for project in data:
            project["modified_by"] = UserModel.get_user_name(project["modified_by"])
            project["created_by"] = UserModel.get_user_name(project["created_by"])
        return data

    @staticmethod
    def get_one_project(project_id, user_id):
        """
        Class method for fetching the details
        of one project based on the project id and user id
        """
        data = ProjectSchema().dump(
            db.session.query(ProjectModel)
            .join(project_member)
            .where(project_member.c.member_id == user_id, ProjectModel.id == project_id)
            .first()
        )
        return data

    @staticmethod
    def get_project_members(project_id):
        """
        Class method for returning all the
        users associated with the project
        """
        data = ProjectSchema().dump(ProjectModel.query.get(project_id))
        data = data["project_members"]
        return data

    @staticmethod
    def is_project_exist(name,organization):
        """
        Class method for checking if a project exists
        by the given name. If yes, then an object of
        ProjectModel is returned else None is returned
        """
        return ProjectModel.query.filter_by(name=name,project_organization=organization).first()

    @staticmethod
    def is_a_member_of_project(project_id, user_id):
        """
        Class method for checking if a user is a
        member of the project or not
        """
        project = ProjectSchema().dump(ProjectModel.query.get(project_id))
        members = project["project_members"]
        for member in members:
            if member["id"] == user_id:
                return True
        return False

    def __repr__(self):
        return f"<id {self.id}>"


class ProjectSchema(Schema):
    """
    Project Schema
    """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    project_admin = fields.Int(required=True)
    project_members = fields.List(fields.Nested(UserSchema(exclude=["password"])))
    project_organization = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int()
    modified_by = fields.Int()
    modified_at = fields.DateTime(dump_only=True)
