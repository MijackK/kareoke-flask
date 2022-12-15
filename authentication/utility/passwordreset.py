import secrets
from app import db
from authentication.models import PasswordReset

def generate_reset_token(email):
    url_token = secrets.token_urlsafe()
    db.session.add(PasswordReset(token = url_token, email = email))
    db.session.commit()
    # send recover url to email
    print(url_token)

def reset_password():
    return "Token is valid password has been reset"
