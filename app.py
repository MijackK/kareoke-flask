import os
from flask import Flask

from authentication.routes import authentication


def create_app():

    # create and configure the app
    app = Flask(__name__)

    app.register_blueprint(authentication, url_prefix='/auth')
    @app.route("/")
    def hello_world():
        return "<p style='color:green'>Hello, World! 3ep</p>"
    
    return app


