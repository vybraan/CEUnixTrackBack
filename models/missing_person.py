from datetime import datetime
from models import db


class MissingPerson(db.Model):
    __tablename__ = 'missing_persons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    lastKnownLocation = db.Column(db.String(100), nullable=False)
    dateOfDisappearance = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
