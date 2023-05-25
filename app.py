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
        supports_credentials=True,
    )
    app.config.from_object("config.Config")

    # connect to database
    db.init_app(app)
    mail.init_app(app)

    from authentication.routes import authentication
    from kareoke.routes import kareoke

    app.register_blueprint(authentication)
    app.register_blueprint(kareoke)

    @app.route("/init", methods=["POST"])
    def hello_init():
        from initilize import create_all

        create_all(db)

        return "initialized"

    return app
