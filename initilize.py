def create_all(db):
    from authentication.models import User
    from werkzeug.security import generate_password_hash

    db.drop_all()
    db.create_all()
    # make admin account
    admin = User(
        username="admin",
        email="admin@gmail.com",
        password=generate_password_hash("admin"),
    )
    admin.admin = True
    admin.verify = True
    db.session.add(admin)
    # commit changes
    db.session.commit()
