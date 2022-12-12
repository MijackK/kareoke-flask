from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    email = db.Column(db.String(60),unique = True)
    password = db.Column(db.String)
    admin = db.Column(db.Boolean, default = False)
    verify = db.Column(db.Boolean, default = False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    token = db.Column(db.String)
    date_created = db.Column(db.String(60),unique = True)
    used = db.Column(db.Boolean, default = False)

    def __init__(self, token):
        self.token = token


class EmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    token = db.Column(db.String)
    date_created = db.Column(db.DateTime, default = datetime.now())
    used = db.Column(db.Boolean, default = False)

    def __init__(self, token):
        self.token = token