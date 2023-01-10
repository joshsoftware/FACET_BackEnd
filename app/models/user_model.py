"""
User module for maintiaing and performing
crud operations on users table in the database.
"""
from datetime import datetime
from marshmallow import Schema, fields
from app.models import db, bcrypt


class UserModel(db.Model):
    """
    User Model
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean)
    is_super_admin = db.Column(db.Boolean)
    user_organization = db.Column(
        db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE")
    )
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor

        The field of is_super_admin is set false by default for every member,
        because there is only one super_admin for the current stage of project
        which is set by the developer
        """
        self.name = data.get("name")
        self.email = data.get("email")
        self.password = self.__generate_hash(data.get("password"))
        self.is_super_admin = False
        self.is_admin = False
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
                if key == "password":
                    self.password = self.__generate_hash(item)
                    item = self.__generate_hash(item)
                setattr(self, key, item)
            self.modified_at = datetime.utcnow()
            db.session.commit()

    def delete(self):
        """
        Class function for deleting an object from  the database
        """
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_users():
        """
        Class method for fetching objects of all users
        """
        return UserModel.query.all()

    @staticmethod
    def get_one_user(user_id):
        """
        Class method for fetching the object
        of one particular user
        """
        return UserModel.query.get(user_id)

    @staticmethod
    def get_user_profile(user):
        """
        Class method for fetching user data
        in json format excluding password
        """
        return UserSchema(exclude=["password"]).dump(user)

    @staticmethod
    def get_user_by_email(email):
        """
        Class method for checking if a user
        exists in the user table for a given
        email id.
        If exists, returns user object
        else return None
        """
        return UserModel.query.filter_by(email=email).first()

    @staticmethod
    def is_super_user(user_id):
        """
        Class method for checking if a user
        is a super admin or not.
        return Boolean type
        """
        user = UserModel.query.get(user_id)
        return user.is_super_admin

    @staticmethod
    def is_user_admin(user_id):
        """
        Class method for checking if a user
        is an admin or not.
        return Boolean type
        """
        user = UserModel.query.get(user_id)
        return user.is_admin

    @staticmethod
    def get_user_name(user_id):
        """
        Class method for fetching
        the name of the user based
        on the given id
        """
        return UserModel.query.get(user_id).name

    @staticmethod
    def get_user_info(user_id):
        """
        Class method for fetching
        the data the of the user in JSON
        format based on the user ID
        """
        return UserSchema(exclude=["password"]).dump(UserModel.query.get(user_id))

    @staticmethod
    def get_all_members():
        """
        Class method for fetching
        the data the of all user in JSON
        format.
        """
        users = UserSchema(exclude=["password"]).dump(UserModel.query.all(), many=True)
        return users

    def __generate_hash(self, password):
        return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")

    def check_hash(self, password):
        """
        function to check if a the provided
        password is valid or invalid
        """
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"<id {self.id}>"


class UserSchema(Schema):
    """
    User Schema
    """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    is_admin = fields.Bool()
    is_super_admin = fields.Bool()
    modified_at = fields.DateTime(dump_only=True)
