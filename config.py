import os


class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI =  os.environ['DATABASE_URL']
    #expiry dates
    SESSION_EXPIRY = "1,day"
    EMAIL_VERIFICATION_TOKEN_EXPIRY = "30,day"
    PASSWORD_RESET_TOKEN_EXPIRY = "1,day"
    #email
    MAIL_SERVER= os.environ['MAIL_SERVER']
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = os.environ['MAIL_USERNAME']
    #rate limiting


class ProductionConfig(Config):
    """Uses production database server."""
    DB_SERVER = '192.168.19.32'

class DevelopmentConfig(Config):
    DB_SERVER = 'localhost'