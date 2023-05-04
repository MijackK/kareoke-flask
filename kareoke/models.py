from app import db
from datetime import datetime
from sqlalchemy import func

class BeatMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    beatMap = db.Column(db.String)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime,default=datetime.now(), onupdate=func.now())

    def __init__(self, name, beatMap, user):
        self.name = name
        self.beatMap = beatMap
        self.user = user


class Background(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    objectID = db.Column(db.String)
    size = db.Column(db.Float)
    beatMap = db.Column(db.Integer, db.ForeignKey("beat_map.id"))

    def __init__(self, name, beatMap, objectID, size):
        self.name = name
        self.beatMap = beatMap
        self.objectID = objectID
        self.size = size


class Audio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    beatMap = db.Column(db.Integer, db.ForeignKey("beat_map.id"))
    objectID = db.Column(db.String)
    size = db.Column(db.Float)

    def __init__(self, name, beatMap, objectID, size):
        self.name = name
        self.beatMap = beatMap
        self.objectID = objectID
        self.size = size
