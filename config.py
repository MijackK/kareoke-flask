import os
from sqlalchemy.engine.url import URL
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = True if os.environ["MODE"] == "development" else False
    CORS_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")
    CORS_SUPPORTS_CREDENTIALS = True
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    # expiry dates
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    EMAIL_VERIFICATION_TOKEN_EXPIRY = "30,day"
    PASSWORD_RESET_TOKEN_EXPIRY = "1,day"
    # email
    MAIL_SERVER = os.environ["MAIL_SERVER"]
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    MAIL_DEFAULT_SENDER = os.environ["MAIL_USERNAME"]
    DRAFT_LIMIT = 2
    MAX_MAP_SIZE = 8000000  # 8MB
    PAGE_LIMIT = 12

    # rate limiting

    # object server
    UPLOAD_BUCKET = "kareoke"


class ProductionConfig(Config):
    """Uses production database server."""

    DB_SERVER = "192.168.19.32"


class DevelopmentConfig(Config):
    DB_SERVER = "localhost"
