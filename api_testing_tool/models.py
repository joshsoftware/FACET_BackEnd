from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    joinedAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    members = db.Column(ARRAY(db.Integer), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
