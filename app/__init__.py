import os
from flask import Flask
from config import app_config
from flask_migrate import Migrate
from flask_cors import CORS
from .models import db, bcrypt
from .routes import *
from dotenv import load_dotenv
load_dotenv()

migrate = Migrate()

def create_app():
    """
        Create App
    """
    env_name = os.getenv('FLASK_ENV')
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    CORS(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    db.app = app
    migrate.init_app(app, db)

    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    app.register_blueprint(projects_blueprint, url_prefix='/api/projects')
    app.register_blueprint(endpoints_blueprint, url_prefix='/api/endpoints')
    app.register_blueprint(headers_blueprint, url_prefix='/api/headers')
    app.register_blueprint(payloads_blueprint, url_prefix='/api/payloads')
    app.register_blueprint(teststeps_blueprint, url_prefix='/api/teststeps')
    app.register_blueprint(testdata_blueprint, url_prefix='/api/testdata')
    app.register_blueprint(testcase_blueprint, url_prefix='/api/testcases')
    app.register_blueprint(env_blueprint, url_prefix='/api/environments')
    app.register_blueprint(engine_blueprint, url_prefix='')
    app.register_blueprint(results_blueprint,url_prefix='/api/results')
    app.register_blueprint(scheduler_blueprint,url_prefix='/api/schedule')

    return app