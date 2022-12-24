from flask_mail import Message
from app import mail

def send_mail(recipient,message):
    msg = Message("hello",recipients=["mijack.kuol@gmail.com"])
    msg.html="""
    <div>
       <h1 style='color:blue'>Congratualations</h1>
       <p> flask mail works</p>
    </div>
    """
    mail.send(msg)
