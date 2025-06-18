# File: app/routes/public.py

from flask import Blueprint, jsonify, current_app
from app.models import Course, Card

public_bp = Blueprint("public", __name__)

@public_bp.route("/api/courses/public", methods=["GET"])
def get_public_courses():
    try:
        public_courses = Course.query.filter_by(is_published=True).order_by(Course.id.desc()).all()
        return jsonify([c.to_dict() for c in public_courses])
    except Exception as e:
        current_app.logger.error(f"Error getting public courses: {str(e)}")
        return jsonify({"error": "Failed to load public courses"}), 500

# --- THÊM 2 ROUTE MỚI Ở DƯỚI ---

@public_bp.route("/api/public/quiz/<int:course_id>", methods=["GET"])
def get_public_quiz_details(course_id):
    """
    Lấy thông tin chi tiết của một quiz đã xuất bản. Bất kỳ ai cũng có thể truy cập.
    """
    try:
        # Chỉ cần kiểm tra quiz có tồn tại và đã xuất bản chưa
        course = Course.query.filter_by(id=course_id, is_published=True).first_or_404()
        return jsonify(course.to_dict())
    except Exception as e:
        return jsonify({"error": "Quiz not found or not published"}), 404

@public_bp.route("/api/public/quiz/<int:course_id>/questions", methods=["GET"])
def get_public_quiz_questions(course_id):
    """
    Lấy tất cả câu hỏi của một quiz đã xuất bản.
    """
    # Kiểm tra xem quiz cha có tồn tại và đã xuất bản không để bảo mật
    course = Course.query.filter_by(id=course_id, is_published=True).first_or_404()
    
    cards = Card.query.filter_by(course_id=course.id).all()
    return jsonify([card.to_dict() for card in cards])