from flask import Blueprint, request, jsonify
from flask_login import current_user
from app.models import db, Card, Course  # Đổi Deck thành Course

cards_bp = Blueprint("cards", __name__)

# Cập nhật card
@cards_bp.route("/cards/<int:card_id>", methods=["PUT"])
def update_card(card_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    course = Course.query.get(card.course_id)
    if not course or course.owner_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json or {}
    card.front = data.get("front", card.front)
    card.back = data.get("back", card.back)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    return jsonify({"message": "Card updated", "card_id": card.id})

# Xóa card
@cards_bp.route("/cards/<int:card_id>", methods=["DELETE"])
def delete_card(card_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    course = Course.query.get(card.course_id)
    if not course or course.owner_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        db.session.delete(card)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    return jsonify({"message": "Card deleted"})
