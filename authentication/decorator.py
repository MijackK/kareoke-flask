from flask import session, request, abort
from authentication.models import User
from functools import wraps


def login_required(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        if "user_id" in session:
            banned = User.query.get(session["user_id"]).banned
            return f" user id is {session.get('user_id')} and cookies are {request.headers.get('Cookie') } csrf {session['csrf_token']} "
            if banned:
                abort(403, "you have been banned, contact admin for resolution")
            csrf_token = request.headers.get("CSRF_TOKEN")
            if csrf_token == session["csrf_token"]:
                return callback(**kwargs)
            print("Cross site attack prevented")
        print("Not allowed, please login")
        abort(401)

    return decorated_function


def require_admin(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        if "user_id" in session:
            is_admin = User.query.get(session["user_id"]).admin
            if is_admin:
                return callback(**kwargs)
        abort(403)

    return decorated_function


def require_verify(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        if "user_id" in session:
            user = User.query.get(session["user_id"])
            print(session["user_id"])
            if user.banned:
                abort(403, "you have been banned, contact admin for resolution")
            if user.verify:
                return callback(**kwargs)
        abort(
            403,
            f"Please verify your email by clicking on the link sent to {user.email}. if no email was sent, navigate to the account option and click the verify button.",
        )

    return decorated_function
