from flask import Blueprint, request, jsonify, current_app
from app.models import db, Course, Card
from app.auth import token_required  # Import decorator token_required

courses_bp = Blueprint("courses", __name__)

# Route tạo khóa học mới
@courses_bp.route("/api/courses", methods=["POST"])
@token_required
def create_course(current_user):
    data = request.json or {}
    name = data.get("name")
    description = data.get("description", "")

    if not name:
        return jsonify({"error": "Course name is required"}), 400

    course = Course(name=name, description=description, owner_id=current_user.id)
    db.session.add(course)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating course: {str(e)}")
        return jsonify({"error": "Database error while creating course", "details": str(e)}), 500

    return jsonify({"message": "Course created successfully", "course": course.to_dict()}), 201

# Route lấy danh sách khóa học của user
@courses_bp.route("/api/courses", methods=["GET"])
@token_required
def get_courses(current_user):
    courses = Course.query.filter_by(owner_id=current_user.id).order_by(Course.created_at.desc()).all()
    return jsonify([c.to_dict() for c in courses])

# Route lấy chi tiết một khóa học
@courses_bp.route("/api/courses/<int:course_id>", methods=["GET"])
@token_required
def get_course(current_user, course_id):
    course = Course.query.filter_by(id=course_id, owner_id=current_user.id).first()

    if not course:
        return jsonify({"error": "Course not found or you don't have permission"}), 404

    cards_data = []
    if hasattr(course, 'cards'):
        cards = Card.query.filter_by(course_id=course.id).all()
        cards_data = [card.to_dict() for card in cards]

    course_data = course.to_dict()
    course_data['cards'] = cards_data
    return jsonify(course_data)

# Route cập nhật khóa học
@courses_bp.route("/api/courses/<int:course_id>", methods=["PUT"])
@token_required
def update_course(current_user, course_id):
    course = Course.query.filter_by(id=course_id, owner_id=current_user.id).first()

    if not course:
        return jsonify({"error": "Course not found or you don't have permission to update"}), 404

    data = request.json or {}
    course.name = data.get("name", course.name)
    course.description = data.get("description", course.description)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating course {course_id}: {str(e)}")
        return jsonify({"error": "Database error while updating course", "details": str(e)}), 500

    return jsonify({"message": "Course updated successfully", "course": course.to_dict()})

# Route xóa khóa học
@courses_bp.route("/api/courses/<int:course_id>", methods=["DELETE"])
@token_required
def delete_course(current_user, course_id):
    course = Course.query.filter_by(id=course_id, owner_id=current_user.id).first()

    if not course:
        return jsonify({"error": "Course not found or you don't have permission to delete"}), 404

    try:
        Card.query.filter_by(course_id=course.id).delete()
        db.session.delete(course)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting course {course_id}: {str(e)}")
        return jsonify({"error": "Database error while deleting course", "details": str(e)}), 500

    return jsonify({"message": "Course deleted successfully"})

# Thêm card vào khóa học
@courses_bp.route("/api/courses/<int:course_id>/cards", methods=["POST"])
@token_required
def add_card_to_course(current_user, course_id):
    course = Course.query.filter_by(id=course_id, owner_id=current_user.id).first()
    if not course:
        return jsonify({"error": "Course not found or you don't have permission to add cards"}), 404

    data = request.json or {}
    front = data.get("front")
    back = data.get("back")

    if not front or not back:
        return jsonify({"error": "Both 'front' and 'back' fields are required for a card"}), 400

    card = Card(front=front, back=back, course_id=course.id)
    db.session.add(card)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding card to course {course_id}: {str(e)}")
        return jsonify({"error": "Database error while adding card", "details": str(e)}), 500

    return jsonify({"message": "Card added successfully", "card": card.to_dict()}), 201

# Lấy tất cả card của khóa học
@courses_bp.route("/api/courses/<int:course_id>/cards", methods=["GET"])
@token_required
def get_cards_for_course(current_user, course_id):
    course = Course.query.filter_by(id=course_id, owner_id=current_user.id).first()
    if not course:
        return jsonify({"error": "Course not found or you don't have permission"}), 404

    cards = Card.query.filter_by(course_id=course.id).all()
    return jsonify([card.to_dict() for card in cards])
