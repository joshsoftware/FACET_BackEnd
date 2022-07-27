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
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor

        The field of is_super_admin is set false by default for every member, because there is only one super_admin for the current stage of project which is set by the developer
        """
        self.name = data.get('name')
        self.email = data.get('email')
        self.password = self.__generate_hash(data.get('password'))
        self.is_super_admin = False
        self.is_admin = False
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data = {}):
        for key, item in data.items():
            if key=='password':
                self.password = self.__generate_hash(item)
            setattr(self, key, item)
        self.modified_at = datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_users():
        return UserModel.query.all()

    @staticmethod
    def get_one_user(id):
        return UserModel.query.get(id)

    @staticmethod
    def get_user_profile(user):
        return UserSchema(exclude=['password']).dump(user)

    @staticmethod
    def get_user_by_email(email):
        return UserModel.query.filter_by(email=email).first()
    
    @staticmethod
    def is_super_user(id):
        user = UserModel.query.get(id)
        return user.is_super_admin
    
    @staticmethod
    def is_user_admin(id):
        user = UserModel.query.get(id)
        return user.is_admin
    
    @staticmethod
    def get_user_name(id):
        return UserModel.query.get(id).name
    
    @staticmethod
    def get_all_members():
        users = UserSchema().dump(UserModel.query.all(),many=True)
        members = []
        for user in users:
            if user['is_super_admin'] == True or user['is_admin'] == True:
                continue
            else:
                members.append(user)
        return members

    def __generate_hash(self, password):
        return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")
    
    def check_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)


    def __repr__(self):
        return '<id {}>'.format(self.id)


    

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