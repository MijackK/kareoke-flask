from flask import Blueprint, jsonify, session, request
from authentication.models import User, PasswordReset, EmailVerification
from app import db
from werkzeug.security import check_password_hash, generate_password_hash
from authentication.decorator import login_required
from authentication.utility.generate_token import (
    generate_reset_token,
    generate_verify_token,
    verify_token,
    generate_csrf_token,
)


authentication = Blueprint("auth", __name__, url_prefix="/auth")


@authentication.route("/login", methods=["POST"])
def login():
    post_data = request.get_json()
    user = User.query.filter(User.email == post_data["email"]).first()
    error_message = {"message": "password or email is incorrect", "success": False}

    if user is None:
        return error_message

    if check_password_hash(user.password, post_data["password"]):
        session.clear()
        session.permanent = True
        session["user_id"] = user.id
        session["csrf_token"] = generate_csrf_token(32)
        info = {
            "userName": user.username,
            "email": user.email,
            "verified": user.verify,
            "csrfToken": session["csrf_token"],
            "success": True,
        }
        return jsonify(info)
    else:
        return error_message


@authentication.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return "succesfully logged out"


@authentication.route("/register", methods=["POST"])
def create_account():
    post_data = request.get_json()
    error_message = {
        "message": "Could not create account, email already in system",
        "success": False,
    }

    # add some validation here for password and email?
    check_exists = User.query.filter(User.email == post_data["email"]).first()

    if check_exists:
        return error_message
    new_user = User(
        username=post_data["userName"],
        email=post_data["email"],
        password=generate_password_hash(post_data["password"]),
    )
    db.session.add(new_user)
    # send verify link to email
    generate_verify_token(post_data["email"])
    db.session.commit()
    return {"message": "account created succesfully", "success": True}


@authentication.route("/generate_verify_url", methods=["POST"])
def generate_verify():
    post_data = request.get_json()
    generate_verify_token(post_data["email"])
    return "verification link sent to email"


@authentication.route("/verify_email", methods=["POST"])
def verify_email():
    post_data = request.get_json()

    response = verify_token(value=post_data["token"], table=EmailVerification)

    if response["success"]:
        user = User.query.filter(User.email == response["email"]).first()
        user.verify = True
        db.session.add(user)
        db.session.commit()
        return "Email Verified"

    return "verification link has expired"


@authentication.route("/generate_reset_url", methods=["POST"])
def new_reset_token():
    generate_reset_token(request.form["email"])
    return "Password Reset url has been sent to your email"


@authentication.route("/recover_password", methods=["POST"])
def password_recovery():
    response = verify_token(value=request.form["token"], table=PasswordReset)

    if response["success"]:
        user = User.query.filter(User.email == response["email"]).first()
        user.password = generate_password_hash(request.form["password"])
        db.session.add(user)
        db.session.commit()
        return "password changed succesfully"

    return "password reset link has expired"


@authentication.route("/check", methods=["GET", "POST"])
@login_required
def check():
    info = User.query.get(session["user_id"])

    return {
        "userName": info.username,
        "email": info.email,
        "verified": info.verify,
        "admin": info.admin,
        "csrfToken": session["csrf_token"],
    }
