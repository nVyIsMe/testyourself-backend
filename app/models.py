from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)  # Google email
    password = db.Column(db.String(200))  # Hashed
    role = db.Column(db.String(10), default="User")  # Admin/User

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    public = db.Column(db.Boolean, default=False)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.Text)
    back = db.Column(db.Text)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    studied = db.Column(db.Integer, default=0)
    correct = db.Column(db.Integer, default=0)
