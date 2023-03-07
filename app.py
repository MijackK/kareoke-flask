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
    from kareoke.routes import kareoke

    app.register_blueprint(authentication)
    app.register_blueprint(kareoke)
    @app.route("/")
    def hello_world():
        return "<p style='color:green'>Hello, World! 3ep</p>"

    @app.route("/init")
    def hello_init():
        from authentication.models import User
        from werkzeug.security import ( generate_password_hash)
        db.drop_all()
        db.create_all()
        admin = User(
            username="admin", 
            email="admin@gmail.com", 
            password=generate_password_hash("admin")
        )
        admin.admin = True
        admin.verify = True
        db.session.add(admin)
        db.session.commit()
        return "initialized"
    
    return app





