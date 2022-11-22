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
    UPLOAD_FOLDER = 'media/excel_files/upload_files'
    DOWNLOAD_FOLDER = 'media/excel_files/download_files'
    MAX_CONTENT_LENGTH = 8*1024*1024
    # ROLLBAR_ACCESS_TOKEN = os.getenv('ROLLBAR_ACCESS_TOKEN')

class Production(object):
    """
    Production environment configurations
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    UPLOAD_FOLDER = 'media/excel_files/upload_files'
    DOWNLOAD_FOLDER = 'media/excel_files/download_files'
    MAX_CONTENT_LENGTH = 8*1024*1024
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES")))
    ROLLBAR_ACCESS_TOKEN = os.getenv('ROLLBAR_ACCESS_TOKEN')

app_config = {
    'development': Development,
    'production': Production,
}
