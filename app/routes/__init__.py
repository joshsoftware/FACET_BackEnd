from flask_jwt_extended import JWTManager

jwt = JWTManager()


from .auth import auth_blueprint
from .projects import projects_blueprint
from .endpoints import endpoints_blueprint
from .headers import headers_blueprint
from .payloads import payloads_blueprint
from .teststeps import teststeps_blueprint
from .testcases import testcase_blueprint
from .testdata import testdata_blueprint
from .engine import engine_blueprint
from .environments import env_blueprint
from .results import results_blueprint
from .scheduler import scheduler_blueprint