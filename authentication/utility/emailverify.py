import secrets
from authentication.models import PasswordReset

def generate_reset_token(email):
    url_token = secrets.token_urlsafe()
 
    print(token)

