from flask_mail import Message
from app import mail


def send_mail(recipient, html, title):
    msg = Message(title, recipients=[recipient])
    msg.html = html
    mail.send(msg)
