from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Deck, Card, User

decks_bp = Blueprint("decks", __name__)

# Create a new deck
@decks_bp.route("/decks", methods=["POST"])
def create_deck():
    """Create a new deck for the current user."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    data = request.json
    name = data.get("name")
    public = data.get("public", False)
    if not name:
        return jsonify({"error": "Deck name is required"}), 400
    deck = Deck(name=name, public=public, owner_id=current_user.id)
    db.session.add(deck)
    db.session.commit()
    return jsonify({"message": "Deck created", "deck_id": deck.id}), 201

# Get all decks for the current user
@decks_bp.route("/decks", methods=["GET"])
def get_decks():
    """Get all decks for the current user."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    decks = Deck.query.filter_by(owner_id=current_user.id).all()
    return jsonify([
        {
            "id": deck.id,
            "name": deck.name,
            "public": deck.public
        } for deck in decks
    ])

# Add a card to a specific deck
@decks_bp.route("/decks/<int:deck_id>/cards", methods=["POST"])
def add_card(deck_id):
    """Add a card to a specific deck."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    data = request.json
    front = data.get("front")
    back = data.get("back")
    if not front or not back:
        return jsonify({"error": "Both 'front' and 'back' fields are required."}), 400
    deck = Deck.query.get(deck_id)
    if not deck or deck.owner_id != current_user.id:
        return jsonify({"error": "Deck not found or unauthorized."}), 404
    card = Card(front=front, back=back, deck_id=deck.id)
    db.session.add(card)
    db.session.commit()
    return jsonify({"message": "Card added", "card_id": card.id}), 201

# Get all cards from a specific deck
@decks_bp.route("/decks/<int:deck_id>/cards", methods=["GET"])
def get_cards(deck_id):
    """Get all cards from a specific deck."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    deck = Deck.query.get(deck_id)
    if not deck or deck.owner_id != current_user.id:
        return jsonify({"error": "Deck not found or unauthorized."}), 404
    cards = Card.query.filter_by(deck_id=deck.id).all()
    return jsonify([
        {
            "id": card.id,
            "front": card.front,
            "back": card.back
        } for card in cards
    ])
