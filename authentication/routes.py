from flask import Blueprint, jsonify, session, request, abort, render_template
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

    if user is None:
        abort(401, "password or email is incorrect")

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
        }
        return jsonify(info)
    abort(401, "password or email is incorrect")


@authentication.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return "succesfully logged out"


@authentication.route("/register", methods=["POST"])
def create_account():
    post_data = request.get_json()

    # add some validation here for password and email?
    check_exists = User.query.filter(User.email == post_data["email"]).first()

    if check_exists:
        abort(409, "Account already exists")
    new_user = User(
        username=post_data["userName"],
        email=post_data["email"],
        password=generate_password_hash(post_data["password"]),
    )
    db.session.add(new_user)
    # send verify link to email
    generate_verify_token(post_data["email"])
    db.session.commit()
    return "account created succesfully"


@authentication.route("/generate_verify_url", methods=["POST"])
@login_required
def generate_verify():
    user = User.query.get(session["user_id"])
    if user.verify:
        return "already verified"
    generate_verify_token(user.email)
    return "verification link sent to email"


@authentication.route("/verify_email", methods=["POST"])
def verify_email():
    post_data = request.get_json()

    user_email = verify_token(value=post_data["token"], table=EmailVerification)

    user = User.query.filter(User.email == user_email).first()
    user.verify = True
    db.session.add(user)
    db.session.commit()
    return "Email Verified"


@authentication.route("/generate_reset_url", methods=["POST"])
def new_reset_token():
    generate_reset_token(request.form["email"])
    return "Password Reset url has been sent to your email"


@authentication.route("/recover_password", methods=["POST"])
def password_recovery():
    user_email = verify_token(value=request.form["token"], table=PasswordReset)

    user = User.query.filter(User.email == user_email).first()
    user.password = generate_password_hash(request.form["password"])
    db.session.add(user)
    db.session.commit()
    return "password changed succesfully"


@authentication.route("/change_password", methods=["POST"])
@login_required
def change_password():
    post_data = request.get_json()
    user = User.query.filter(User.email == post_data["email"]).first()
    if check_password_hash(user.password, post_data["currentPassword"]):
        user.password = generate_password_hash(post_data["newPassword"])
        db.session.commit()
        return "Password sucessfully changed"
    abort(401, description="current password incorrect")


@authentication.route("/change_acount_info", methods=["POST"])
@login_required
def change_account_info():
    editable_info = ["email", "username"]
    post_data = request.get_json()
    if post_data["column"] not in editable_info:
        abort(403)
    user = User.query.filter(User.email == post_data["email"]).first()
    if check_password_hash(user.password, post_data["password"]):
        setattr(user, post_data["column"], post_data["value"])
        if post_data["column"] == "email":
            user.verify = False
        db.session.commit()
        return "Password sucessfully changed"
    abort(401, description="password incorrect")


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
