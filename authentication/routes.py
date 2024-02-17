from flask import (
    Blueprint,
    current_app,
    jsonify,
    session,
    request,
    abort,
    render_template,
)
import os
from authentication.models import User, TokenVerification
from app import db, limiter
from werkzeug.security import check_password_hash, generate_password_hash
from authentication.decorator import login_required, require_admin
from authentication.utility.generate_token import (
    generate_token,
    verify_token,
    generate_csrf_token,
)
from authentication.utility.email import send_mail
from authentication.utility.verification import verify_password, email_verification


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

    if not email_verification(post_data["email"]):
        abort(400, "invalid email")
    if not verify_password(post_data["password"]):
        abort(
            400,
            "password must have, more that 8 characters, atleast one uppercase letter, lowercase letter, number and special character",
        )

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
    db.session.commit()

    token = generate_token(email=post_data["email"], type="email")
    url = f"{os.environ['FRONTEND_DOMAIN']}/verifyemail.html?token={token}"
    if current_app.config["DEBUG"]:
        print(url)
        return url

    send_mail(
        post_data["email"],
        render_template("verify_email.html", token_url=url),
        "Verify Email",
    )

    return "account created succesfully"


@authentication.route("/generate_verify_url", methods=["POST"])
@limiter.limit("10 per day")
@login_required
def generate_verify():
    user = User.query.get(session["user_id"])
    if user.verify:
        return "already verified"
    token = generate_token(email=user.email, type="email")
    url = f"{os.environ['FRONTEND_DOMAIN']}/verifyemail.html?token={token}"
    if current_app.config["DEBUG"]:
        print(url)
        return url
    send_mail(
        user.email,
        render_template("verify_email.html", token_url=url),
        "Verify Email",
    )
    return "verification link sent to email"


@authentication.route("/verify_email", methods=["POST"])
def verify_email():
    post_data = request.get_json()

    user_email = verify_token(value=post_data["token"], type="email")

    user = User.query.filter(User.email == user_email).first()
    user.verify = True
    db.session.add(user)
    db.session.commit()
    return "Email Verified"


@authentication.route("/generate_reset_url", methods=["POST"])
@limiter.limit("10 per day")
def new_reset_token():
    token = generate_token(email=request.form["email"], type="password")
    url = f"{os.environ['FRONTEND_DOMAIN']}/passwordreset.html?token={token}"

    if current_app.config["DEBUG"]:
        print(url)
        return url
    send_mail(
        recipient=request.form["email"],
        html=render_template(
            "password_reset_email.html",
            token_url=url,
        ),
        title="Password Reset",
    )

    return "Password Reset url has been sent to your email"


@authentication.route("/recover_password", methods=["POST"])
def password_recovery():
    user_email = verify_token(value=request.form["token"], type="password")
    if not verify_password(request.form["password"]):
        abort(400, "password not strong enough")
    user = User.query.filter(User.email == user_email).first()
    user.password = generate_password_hash(request.form["password"])
    db.session.add(user)
    db.session.commit()
    return "password changed succesfully"


@authentication.route("/change_password", methods=["POST"])
@login_required
def change_password():
    post_data = request.get_json()
    if not verify_password(post_data["newPassword"]):
        abort(400, "password not strong enough")

    user = User.query.get(session["user_id"])
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
    user = user = User.query.get(session["user_id"])
    if check_password_hash(user.password, post_data["password"]):
        setattr(user, post_data["column"], post_data["value"])
        if post_data["column"] == "email":
            user.verify = False
        db.session.commit()
        return "Password sucessfully changed"
    abort(401, description="password incorrect")


@authentication.route("/ban", methods=["POST"])
@require_admin
def ban():
    post_data = request.get_json()
    user = User.query.get(post_data["user"])
    if user is None:
        abort(404, "user doesnt exist")
    if user.banned:
        return "user already banned"
    user.banned = post_data["reason"]
    db.session.commit()

    return f"user {user.username} is banned"


@authentication.route("/unban", methods=["POST"])
@require_admin
def unban():
    post_data = request.get_json()
    user = User.query.get(post_data["user"])
    if user is None:
        abort(404, "user doesnt exist")
    if user.banned is None:
        return "user not banned"
    user.banned = None
    db.session.commit()

    return f"user {user.username} is unbanned"


@authentication.route("/get_users", methods=["GET"])
@require_admin
def get_users():
    users = User.query.filter(User.admin == False).all()
    user_list = []

    for user in users:
        user_list.append(
            {"id": user.id, "username": user.username, "banned": user.banned}
        )

    return user_list


@authentication.route("/check", methods=["GET", "POST"])
@login_required
def check():
    info = (
        User.query.outerjoin(TokenVerification, TokenVerification.email == User.email)
        .with_entities(
            User.username.label("username"),
            User.email.label("email"),
            User.verify.label("verify"),
            User.admin.label("admin"),
            TokenVerification.used.label("used"),
        )
        .filter(TokenVerification.type == "email", User.id == session["user_id"])
        .order_by(TokenVerification.date_created.desc())
        .first()
    )

    return {
        "userName": info.username,
        "email": info.email,
        "verified": info.verify,
        "admin": info.admin,
        "csrfToken": session["csrf_token"],
        "used": info.used if info.used is not None else True,
    }
