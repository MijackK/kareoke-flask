import secrets
import os
from app import db
from authentication.models import PasswordReset, EmailVerification
from flask import abort, render_template
from authentication.utility.email import send_mail


# for password reset
def generate_reset_token(email):
    # check if user exist?
    url_token = secrets.token_urlsafe()
    db.session.add(PasswordReset(token=url_token, email=email))
    db.session.commit()
    # send recover url to email?
    reset_url = f"{os.environ['DOMAIN']}/passwordreset.html?token={url_token}"
    send_mail(
        recipient=email,
        html=render_template(
            "password_reset_email.html",
            token_url=reset_url,
        ),
        title="Password Reset",
    )


# for email verification
def generate_verify_token(email):
    # check if user exists?
    # check is account is allready verified
    url_token = secrets.token_urlsafe()
    db.session.add(EmailVerification(token=url_token, email=email))
    db.session.commit()
    # send verify url to email?
    token_url = f"{os.environ['DOMAIN']}/verifyemail.html?token={url_token}"
    send_mail(
        email, render_template("verify_email.html", token_url=token_url), "Verify Email"
    )


def verify_token(value, table):
    token = (
        table.query.filter(table.token == value, table.used == False)
        .order_by(table.date_created.desc())
        .first()
    )
    if token is None:
        abort(404, description="verify token is invalid")
    if token.is_valid():
        token.used = True
        db.session.add(token)

    return token.email


def generate_csrf_token(length):
    return secrets.token_urlsafe(length)
