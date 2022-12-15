import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy





db = SQLAlchemy()

def create_app():
    
    # create and configure the app
    app = Flask(__name__)

    #connect to database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.secret_key="secret"
    db.init_app(app)

 


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





