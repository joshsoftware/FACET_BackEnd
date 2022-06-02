from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# # DB config Data
# MONGO_URI = os.getenv("MONGO_URI")
# MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST")
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = os.getenv("DB_NAME")


# # Secret Key
# SECRET_KEY = os.getenv("SECRET_KEY")
# JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# import os

class Development(object):
    """
    Development environment configuration
    """
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class Production(object):
    """
    Production environment configurations
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES")

app_config = {
    'development': Development,
    'production': Production,
}
