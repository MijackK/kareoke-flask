from app import db
from datetime import datetime
from sqlalchemy import func


class BeatMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    beatMap = db.Column(db.String)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=func.now())
    background = db.relationship("Background", cascade="all, delete")
    audio = db.relationship("Audio", cascade="all, delete")
    highscore = db.relationship("HighScore", cascade="all, delete")
    mapedits = db.relationship("MapEdits", cascade="all, delete")

    def __init__(self, name, beatMap, user):
        self.name = name
        self.beatMap = beatMap
        self.user = user


class Background(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    objectID = db.Column(db.String)
    size = db.Column(db.Float)
    beatMap = db.Column(db.Integer, db.ForeignKey("beat_map.id"), index=True)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, name, beatMap, objectID, size):
        self.name = name
        self.beatMap = beatMap
        self.objectID = objectID
        self.size = size


class Audio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    beatMap = db.Column(db.Integer, db.ForeignKey("beat_map.id"), index=True)
    objectID = db.Column(db.String)
    size = db.Column(db.Float)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, name, beatMap, objectID, size):
        self.name = name
        self.beatMap = beatMap
        self.objectID = objectID
        self.size = size


class HighScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    beatMap = db.Column(db.Integer, db.ForeignKey("beat_map.id"), index=True)
    score = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=func.now())

    def __init__(self, beatMap, score, user):
        self.beatMap = beatMap
        self.score = score
        self.user = user


class MapEdits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beatMap = db.Column(db.Integer, db.ForeignKey("beat_map.id"), index=True)
    targetID = db.Column(db.String)
    table = db.Column(db.String)
    column = db.Column(db.String)
    action = db.Column(db.String)
    value = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=func.now())
