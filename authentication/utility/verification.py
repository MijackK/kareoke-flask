import re


def verify_password(password):
    password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    valid = re.match(password_pattern, password)
    if valid is None:
        return False
    return True


def email_verification(email):
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    valid = re.match(email_pattern, email)
    if valid is None:
        return False
    return True
