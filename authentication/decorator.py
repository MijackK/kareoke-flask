from flask import session, request, abort
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
            print("Cross site attack prevented")
            abort(401)
        print("Not allowed, please login")
        abort(401)
    return decorated_function

def require_admin(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        if "user_id" in session:
            is_admin = User.query.get(session['user_id']).admin
            if(is_admin):
                return callback(**kwargs)
        print("Only administrator is allowed")
        abort(403)
    return decorated_function
            
def require_verify(callback):
    @wraps(callback)
    def decorated_function(**kwargs):
        if "user_id" in session:
            is_verified = User.query.get(session['user_id']).verify
            if(is_verified):
                return callback(**kwargs)
        print("Please verify your email first")
        abort(403)
    return decorated_function


