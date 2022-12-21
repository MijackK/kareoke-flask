import secrets
import string
from app import db
from authentication.models import PasswordReset, EmailVerification

#for password reset
def generate_reset_token(email):
    #check if user exist?
    url_token = secrets.token_urlsafe()
    db.session.add(PasswordReset(token = url_token, email = email))
    db.session.commit()
    # send recover url to email?
    print(url_token)

#for email verification
def generate_verify_token(email):
    #check if user exists?
    #check is account is allready verified
    url_token = secrets.token_urlsafe()
    db.session.add(EmailVerification(token = url_token, email = email))
    db.session.commit()
    # send verify url to email?
    print(url_token)

def verify_token(value, table):
    token = (
        table.query
        .filter(table.token == value )
        .order_by(table.date_created.desc())
        .first()
    )
    response = {"success":False,"email":None}
    if token == None:
        return response
    if token.is_valid():
        token.used = True
        db.session.add(token)
        response['success'] = True
        response['email'] = token.email

    return response

def generate_csrf_token(length):
    return secrets.token_urlsafe(length)

