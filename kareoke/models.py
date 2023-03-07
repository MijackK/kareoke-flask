from app import db
class BeatMap(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    background = db.Column(db.String,unique = True)
    audio = db.Column(db.String,unique = True)
    beats = db.Column(db.String)
    User = db.Column(db.Integer,ForeignKey("user.id"))
 

    def __init__(self, name, audio, background):
        self.name = name
        self.audio = audio
        self.background = background

