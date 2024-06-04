from flask import abort
import secrets

from app import db
from authentication.models import (
    User,
    TokenVerification,
)


def generate_csrf_token(length):
    return secrets.token_urlsafe(length)


def generate_token(email, type):
    user = User.query.filter(User.email == email).first()
    if not user:
        abort(404)
    recent_token = (
        TokenVerification.query.filter(
            TokenVerification.email == email,
            TokenVerification.used == False,
            TokenVerification.type == type,
        )
        .order_by(TokenVerification.date_created.desc())
        .first()
    )
    if recent_token:
        recent_token.used = True

    url_token = secrets.token_urlsafe()
    db.session.add(TokenVerification(token=url_token, email=email, type=type))
    db.session.commit()
    # send recover url to email?
    return url_token


def verify_token(value, type):
    token = (
        TokenVerification.query.filter(
            TokenVerification.token == value,
            TokenVerification.used == False,
            TokenVerification.type == type,
        )
        .order_by(TokenVerification.date_created.desc())
        .first()
    )
    is_valid = False
    if token:
        is_valid = token.is_valid()
    if not is_valid:
        abort(404, description="verify token is expired or used")

    token.used = True
    db.session.add(token)

    return token.email
