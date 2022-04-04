from api_testing_tool import app

from .auth import auth_blueprint
app.register_blueprint(auth_blueprint)

from .projects import projects_blueprint
app.register_blueprint(projects_blueprint)

from .endpoints import endpoints_blueprint
app.register_blueprint(endpoints_blueprint)

from .headers import headers_blueprint
app.register_blueprint(headers_blueprint)

