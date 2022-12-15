from flask import Blueprint, jsonify, session, request
from authentication.models import User,PasswordReset,EmailVerification
from app import db
from werkzeug.security import check_password_hash, generate_password_hash
from authentication.decorator import  login_required
from authentication.utility.generate_token import (
    generate_reset_token, 
    generate_verify_token, 
    verify_token
)



authentication = Blueprint("/auth", __name__, url_prefix='/auth')


@authentication.route("/login", methods=['POST'] )
def login():
 
    user = User.query.filter(User.email == request.form['email']).first()
    my_id = None
    if "user_id" in session:
        my_id = session['user_id']
   
    if user == None:
        return "password or email is incorrect"

    if check_password_hash(user.password,request.form['password']):
        session.clear()
        session['user_id'] = user.id
        info = {
            "userName":user.username,
            "email":user.email,
            "verified":user.verify
        }
        return jsonify(info)
    else:
        return "password or email is incorrect"


    return f"user name is {user.username} & email is {user.email}"

@authentication.route("/logout")
def logout():
    session.clear()
    return "succesfully logged out"

@authentication.route("/register", methods=['POST'])
def create_account():

    #add some validation here for password and email?
    check_exists = User.query.filter(User.email == request.form["email"]).first()
 
    if check_exists:
        return "Could not create account, email already in system"
    new_user = User(
        username = request.form["userName"], 
        email = request.form["email"], 
        password =  generate_password_hash(request.form["password"])
    )
    db.session.add(new_user)
    #send verify link to email
    generate_verify_token(request.form["email"])
    db.session.commit()
    return "create"

@authentication.route("/generate_verify_url", methods=['POST'])
def generate_verify():
    generate_verify_token(request.form["email"])
    return "verification link sent to email"



@authentication.route("/verify_email", methods=['POST'])
def verify_email():
    post_data = request.get_json()

    response = verify_token(value = post_data['token'], table = EmailVerification)

    if response["success"]:
        user = User.query.filter(User.email == response["email"]).first()
        user.verify = True
        db.session.add(user)
        db.session.commit()
        return "Email Verified"

    return "verification link has expired"

@authentication.route("/generate_reset_url", methods=['POST'])
def new_reset_token():
    generate_reset_token(request.form["email"])
    return "Password Reset url has been sent to your email"

@authentication.route("/recover_password", methods=['POST'])
def password_recovery():
   
    response = verify_token(value = request.form["token"], table = PasswordReset)

    if response["success"]:
        user = User.query.filter(User.email == response["email"]).first()
        user.password = generate_password_hash(request.form["password"])
        db.session.add(user)
        db.session.commit()
        return "password changed succesfully" 

    return "password reset link has expired"


@authentication.route("/edit", methods=['GET','POST'])
@login_required
def info_edit():
    return "you are logged in"