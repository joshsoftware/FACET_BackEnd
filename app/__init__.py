from flask import Flask
from config import app_config
from flask_migrate import Migrate

from .models import db, bcrypt
from .routes import *


migrate = Migrate()

def create_app(env_name):
    """
        Create App
    """
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    app.register_blueprint(projects_blueprint, url_prefix='/api/projects')
    app.register_blueprint(endpoints_blueprint, url_prefix='/api/endpoints')

    return app