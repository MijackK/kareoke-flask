import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail


db = SQLAlchemy()
mail = Mail()

def create_app():
    # create and configure the app
    app = Flask(__name__)
    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:8080"}},
        supports_credentials=True
    )
    app.config.from_object("config.Config")


    #connect to database
    db.init_app(app)
    mail.init_app(app)
    

    from authentication.routes import authentication

    app.register_blueprint(authentication)
    @app.route("/")
    def hello_world():
        return "<p style='color:green'>Hello, World! 3ep</p>"

    @app.route("/init")
    def hello_init():
        db.drop_all()
        db.create_all()
        return "initialized"
    
    return app





