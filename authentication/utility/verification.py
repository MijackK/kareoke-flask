import re


def verify_password(password):
    if len(password) < 8:
        return False

    has_digit = False
    has_uppercase = False

    for char in password:
        if char.isdigit():
            has_digit = True
        elif char.isupper():
            has_uppercase = True
        if has_digit and has_uppercase:
            break

    if not has_digit or not has_uppercase:
        return False

    return True


def email_verification(email):
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    valid = re.match(email_pattern, email)
    if valid is None:
        return False
    return True
