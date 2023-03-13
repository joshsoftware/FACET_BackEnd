from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

class Development(object):
    """
    Development environment configuration
    """
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES")))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER= os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    # CELERY_BROKER_URL = 'redis://localhost:6379/0'
    # CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    # ROLLBAR_ACCESS_TOKEN = os.getenv('ROLLBAR_ACCESS_TOKEN')

class Production(object):
    """
    Production environment configurations
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES")))
    ROLLBAR_ACCESS_TOKEN = os.getenv('ROLLBAR_ACCESS_TOKEN')
    MAIL_SERVER= os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    FRONTEND_URL = os.getenv("FRONTEND_URL")

app_config = {
    'development': Development,
    'production': Production,
}

logger_config = {
    'version': 1,
    'formatters': {'default': {
        'format' : '%(asctime)s | %(levelname)-8s | %(message)s',
    },
    'development': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    }},
    'handlers': {'development': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'development',
        'level': 'DEBUG'
    },
    'production':{
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': 'records.log',
        'when' : 'D',
        'interval' : 30,
        'backupCount' : 12,
        'formatter': 'default',
        'level' : 'INFO'
    }},
    'root': {
        'level' : 'DEBUG',
        'handlers': [os.getenv('FLASK_ENV')]
    }
}
