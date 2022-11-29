from flask import Blueprint
from authentication.models import User
from app import db



authentication = Blueprint("/auth", __name__, url_prefix='/auth')

@authentication.route("/login")
def login():
    user = User.query.get(1)

    return f"user name is {user.username} & email is {user.email}"

@authentication.route("/logout")
def logout():
    return "logout"

@authentication.route("/create")
def create_account():
    return "create"

@authentication.route("/verify")
def verify():
    return "verify"

@authentication.route("/recover")
def password_recovery():
    return "recover"

@authentication.route("/edit")
def info_edit():
    return "info"