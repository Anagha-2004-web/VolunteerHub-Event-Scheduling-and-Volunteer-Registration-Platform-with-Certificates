# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Organizer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(128))
    # add more fields if needed

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(50))
    points = db.Column(db.Integer, default=0)
    joinedDate = db.Column(db.Date)
    eventsCompleted = db.Column(db.Integer, default=0)
    emergencyContact = db.Column(db.String(120))
    interests = db.Column(db.Text)
    skills = db.Column(db.Text)

class Event(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    title = db.Column(db.String(120))
    date = db.Column(db.String(24))
    time = db.Column(db.String(12))
    endTime = db.Column(db.String(12))
    description = db.Column(db.Text)
    budget = db.Column(db.String(32))
    location = db.Column(db.String(128))
    status = db.Column(db.String(24))
    category = db.Column(db.String(50))
    qrCode = db.Column(db.String(60))
    createdAt = db.Column(db.String(30))

class Signup(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    eventId = db.Column(db.String(40), db.ForeignKey('event.id'))
    volunteerId = db.Column(db.Integer, db.ForeignKey('volunteer.id'))
    volunteerName = db.Column(db.String(120))
    volunteerEmail = db.Column(db.String(120))
    role = db.Column(db.String(32))
    signupDate = db.Column(db.String(30))
    status = db.Column(db.String(12))
    attended = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    type = db.Column(db.String(32))
    message = db.Column(db.Text)
    email = db.Column(db.String(120))
    timestamp = db.Column(db.String(30))
    read = db.Column(db.Boolean, default=False)

class SwapRequest(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    fromSignupId = db.Column(db.String(40))
    toSignupId = db.Column(db.String(40))
    eventId = db.Column(db.String(40))
    status = db.Column(db.String(24))
