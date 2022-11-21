from app import create_app
app = create_app()
app.app_context().push()

import os
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception

@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    if not (app.config['ENV'] == "development"):
        rollbar.init(
            # access token
            app.config['ROLLBAR_ACCESS_TOKEN'],
            # environment name
            os.getenv('FLASK_ENV'),
            # server root directory, makes tracebacks prettier
            root=os.path.dirname(os.path.realpath(__file__)),
            # flask already sets up logging
            allow_logging_basic_config=False)

        # send exceptions from `app` to rollbar, using flask's signal system.
        got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

if __name__=='__main__':
    app.run()   