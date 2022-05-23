from flask import Flask
from config import app_config
from flask_migrate import Migrate

from .models import db, bcrypt


migrate = Migrate()

def create_app(env_name):
    """
        Create App
    """
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    return app