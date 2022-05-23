import os
from app import create_app, db
# from dotenv import load_dotenv
# load_dotenv()

if __name__=='__main__':
    env_name = os.getenv('FLASK_ENV')
    app = create_app(env_name)
    app.run()