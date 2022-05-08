from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import *
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
 
app = Flask(__name__)
CORS(app)
app.secret_key = SECRET_KEY

jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(JWT_ACCESS_TOKEN_EXPIRES))

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
# client = MongoClient(MONGO_URI)
# db = client[MONGO_DB_NAME]

from .routes import *
from .models import *
