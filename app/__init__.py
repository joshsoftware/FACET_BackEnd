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
    app.register_blueprint(headers_blueprint, url_prefix='/api/headers')
    app.register_blueprint(payloads_blueprint, url_prefix='/api/payloads')
    app.register_blueprint(testcases_blueprint, url_prefix='/api/testcases')
    app.register_blueprint(testdata_blueprint, url_prefix='/api/testdata')
    app.register_blueprint(testsuite_blueprint, url_prefix='/api/testsuites')
    app.register_blueprint(env_blueprint, url_prefix='/api/environments')
    app.register_blueprint(engine_blueprint, url_prefix='')

    return app