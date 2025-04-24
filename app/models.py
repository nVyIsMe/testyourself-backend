from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Required for Google login
    name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200))

    def __repr__(self):
        return f'<User {self.email}>'

    """User model for storing user details."""

class Deck(db.Model):
    __tablename__ = 'decks'
    """Deck model representing a collection of cards."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    public = db.Column(db.Boolean, default=False)

class Card(db.Model):
    __tablename__ = 'cards'
    """Card model for front and back content."""
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.Text)
    back = db.Column(db.Text)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'))

class Progress(db.Model):
    __tablename__ = 'progress'
    """Progress model for user study tracking."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'))
    studied = db.Column(db.Integer, default=0)
    correct = db.Column(db.Integer, default=0)
