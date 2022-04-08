from dotenv import load_dotenv
import os

load_dotenv()

# DB config Data
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST_NAME = os.getenv("MONGO_HOST_NAME")
MONGO_HOST_PORT = os.getenv("MONGO_HOST_PORT")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Secret Key
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES")