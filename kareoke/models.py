from app import db
from datetime import datetime
from sqlalchemy import func


class BeatMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    beatMap = db.Column(db.String)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    status = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=func.now())
    date_updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def __init__(self, name, beatMap, user, status="draft"):
        self.name = name
        self.beatMap = beatMap
        self.user = user
        self.status = status


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    objectID = db.Column(db.String)
    size = db.Column(db.Float)
    beatMap = db.Column(
        db.Integer, db.ForeignKey("beat_map.id", ondelete="CASCADE"), index=True
    )
    date_created = db.Column(db.DateTime, default=func.now())
    type = db.Column(db.String)

    def __init__(self, beatMap, objectID, size, type):
        self.beatMap = beatMap
        self.objectID = objectID
        self.size = size
        self.type = type


class HighScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    beatMap = db.Column(
        db.Integer, db.ForeignKey("beat_map.id", ondelete="CASCADE"), index=True
    )
    score = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=func.now())
    date_updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def __init__(self, beatMap, score, user):
        self.beatMap = beatMap
        self.score = score
        self.user = user
