from flask import Blueprint

authentication = Blueprint("/auth", __name__)

@authentication.route("/login")
def login():
    return "login"

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