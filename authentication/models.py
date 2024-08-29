from app import db
from datetime import datetime
from sqlalchemy import func


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String(60), unique=True)
    password = db.Column(db.String)
    admin = db.Column(db.Boolean, default=False)
    verify = db.Column(db.Boolean, default=False)
    banned = db.Column(db.String, default=None)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class TokenVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60))
    token = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=func.now())
    date_updated = db.Column(db.DateTime, onupdate=func.now())
    used = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(60))

    def __init__(self, token, email, type):
        self.token = token
        self.email = email
        self.type = type

    def is_valid(self):
        current_time = func.now()()
        delta = current_time - self.date_created
        hours = delta.total_seconds() / 3600
        # change it so we get the hours limit from the config
        if hours < 24 and not self.used:
            return True
        if not self.used:
            self.used = True
            db.session.commit()
        return False


class AccessControl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    permission = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=func.now())

    def __init__(self, user, permission):
        self.user = user
        self.permission = permission


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    read = db.Column(db.Boolean, default=False)
    user = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    date_created = db.Column(db.DateTime, default=func.now())

    def __init__(self, user, message):
        self.user = user
        self, message = message
