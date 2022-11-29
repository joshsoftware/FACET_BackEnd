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

app_config = {
    'development': Development,
    'production': Production,
}

logger_config = {
    'version': 1,
    'formatters': {'default': {
        'format' : '%(asctime)s | %(levelname)-8s | %(filename)s-%(funcName)s-%(lineno)04d | %(message)s',
    },
    'development': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    }},
    'handlers': {'development': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'development'
    },
    'production':{
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': 'records.log',
        'mode': 'a',
        'maxBytes': 1024*1024*8,
        'backupCount' : 5,
        'formatter': 'default',
        'level' : 'INFO'
    }},
    'root': {
        'level' : 'DEBUG',
        'handlers': [os.getenv('FLASK_ENV')]
    }
}
