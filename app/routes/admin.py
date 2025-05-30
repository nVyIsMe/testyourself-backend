from flask import Blueprint, request, jsonify
from flask_login import current_user
from app.models import db, User, Course, Card  # Đổi Deck thành Course

admin_bp = Blueprint("admin", __name__)

# Middleware kiểm tra quyền admin
def require_admin():
    if not current_user.is_authenticated or current_user.role != "ADMIN":
        return jsonify({"error": "Admin only"}), 403

# GET /admin/users - lấy danh sách người dùng
@admin_bp.route("/users", methods=["GET"])
def get_users():
    error = require_admin()
    if error: 
        return error

    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role
        } for u in users
    ])

# PUT /admin/users/<id>/ban - khóa hoặc mở user
@admin_bp.route("/users/<int:user_id>/ban", methods=["PUT"])
def toggle_user_ban(user_id):
    error = require_admin()
    if error:
        return error

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == "ADMIN":
        return jsonify({"error": "Cannot ban admin"}), 403

    user.role = "BANNED" if user.role != "BANNED" else "USER"
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    return jsonify({"message": f"User role set to {user.role}"})

# DELETE /admin/flashcards/<id> - xoá course vi phạm (thay vì deck)
@admin_bp.route("/flashcards/<int:course_id>", methods=["DELETE"])
def delete_course_by_admin(course_id):
    error = require_admin()
    if error:
        return error

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Xoá thẻ trước rồi xoá course
    Card.query.filter_by(course_id=course.id).delete()
    db.session.delete(course)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    return jsonify({"message": "Course deleted by admin"})
