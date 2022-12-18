from flask import session, request
from app import db
from authentication.models import User
from functools import wraps

def login_required(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        if "user_id" in session:
            csrf_token = request.headers.get("CSRF_TOKEN")
            if csrf_token == session['csrf_token']:
                return callback(**kwargs)
            return "Cross site attack prevented"
        return "Not allowed, please login"
    return decorated_function

def require_admin(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        if "user_id" in session:
            is_admin = User.query.get(session['user_id']).admin
            if(is_admin):
                return callback(**kwargs)
        return "Only administrator is allowed"
    return decorated_function
            
def require_verify(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        if "user_id" in session:
            is_verified = User.query.get(session['user_id']).verify
            if(is_verified):
                return callback(**kwargs)
        return "Please verify your email first"
    return decorated_function

def session_expiry(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        print("session expiry check")
        return callback(**kwargs)
    return decorated_function
