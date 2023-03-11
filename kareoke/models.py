from app import db

class BeatMap(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    background = db.Column(db.String, db.ForeignKey("media.id"))
    audio = db.Column(db.String, db.ForeignKey("media.id"))
    songMap = db.Column(db.String)
    user = db.Column(db.Integer,db.ForeignKey("user.id"))
 

    def __init__(self, name, audio, background, song_map):
        self.name = name
        self.audio = audio
        self.background = background
        self.songMap = song_map 
        self.user = 1

class Media(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String)
    bucket = db.Column(db.String, db.ForeignKey("bucket.id"))
    isBackground = db.Column(db.Boolean)

    def __init__(self, name, bucket, isBackground):
        self.name = name
        self.bucket = bucket
        self.isBackground = isBackground

class Bucket(db.Model):
    id =  db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
    
