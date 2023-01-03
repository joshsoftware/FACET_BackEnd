"""
OrganizationUser Class module for capturing many to many
relationship between user and organization,
while maitaining the privilege level for each user.
"""

from marshmallow import fields, Schema

from app.models.UserModel import UserSchema

from app.models import db


class OrganizationUserModel(db.Model):
    """
    association table for organization and user with privilege level.
    """

    __tablename__ = "organization_user"

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    privilege_level = db.Column(db.String(50), nullable=False)

    def __init__(self, data):
        self.organization_id = data.get("organization_id")
        self.user_id = data.get("user_id")
        self.privilege_level = data.get("privilege_level")

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

    def __repr__(self):
        return f"<id {self.id}>"

    @staticmethod
    def get_all_org_users(organization_id):
        """
        static method for fetching all users of a particular organization
        """
        data = OrganizationUserModel.query.filter_by(organization_id=organization_id)
        for user in data:
            print(user)


class OrganizationUserSchema(Schema):
    """
    Organization User Schema
    """

    user = fields.Nested(UserSchema(exclude=["password"]))
    privilege_level = fields.Str()
