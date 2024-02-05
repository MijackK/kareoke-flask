from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


db = SQLAlchemy()
mail = Mail()


def create_app(environ, start_response):
    # create and configure the app
    app = Flask(__name__)
    limiter = Limiter(
        get_remote_address,
        app=app,
    )
    app.config.from_object("config.Config")

    CORS(app)

    # connect to database
    db.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    """ 
    from authentication.routes import authentication
    from kareoke.routes import kareoke

    app.register_blueprint(authentication)
    app.register_blueprint(kareoke)

    @app.route("/init", methods=["POST"])
    def hello_init():
        from authentication.models import User
        from werkzeug.security import generate_password_hash
        from flask import current_app

        if not current_app.config["DEBUG"]:
            db.create_all()
            db.session.commit()
            return "database tables created"

        db.drop_all()
        db.create_all()
        # make admin account
        admin = User(
            username="admin",
            email="admin@gmail.com",
            password=generate_password_hash("admin"),
        )
        admin.admin = True
        admin.verify = True
        db.session.add(admin)
        # commit changes
        db.session.commit()
        return "initialized" 
    """

    return app
