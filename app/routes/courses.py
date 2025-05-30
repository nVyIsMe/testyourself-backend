# app/routes/courses.py

from flask import Blueprint, request, jsonify
from app.models import db, Course, Card # Đảm bảo Card được import nếu bạn dùng nó
from app.auth import token_required # Quan trọng: import decorator của bạn

courses_bp = Blueprint("courses", __name__)

# === COURSE ROUTES ===

# Tạo khóa học mới
@courses_bp.route("/courses", methods=["POST"])
@token_required
def create_course(current_user): # Nhận current_user từ decorator
    data = request.json or {}
    name = data.get("name")
    description = data.get("description", "")

    if not name:
        return jsonify({"error": "Course name is required"}), 400

    # Kiểm tra xem tên khóa học đã tồn tại bởi user này chưa (tùy chọn, nếu cần)
    # existing_course = Course.query.filter_by(name=name, owner_id=current_user.id).first()
    # if existing_course:
    #     return jsonify({"error": "You already have a course with this name"}), 400

    course = Course(name=name, description=description, owner_id=current_user.id)
    db.session.add(course)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating course: {str(e)}") # Log lỗi
        return jsonify({"error": "Database error while creating course", "details": str(e)}), 500

    return jsonify({"message": "Course created successfully", "course": course.to_dict()}), 201

# Lấy danh sách tất cả khóa học của user đang đăng nhập
@courses_bp.route("/courses", methods=["GET"])
@token_required
def get_courses(current_user):
    courses = Course.query.filter_by(owner_id=current_user.id).order_by(Course.created_at.desc()).all()
    return jsonify([c.to_dict() for c in courses])

# Lấy chi tiết một khóa học (bao gồm cả cards nếu có)
@courses_bp.route("/courses/<int:course_id>", methods=["GET"])
@token_required
def get_course(current_user, course_id):
    course = Course.query.filter_by(id=course_id, owner_id=current_user.id).first()

    if not course:
        return jsonify({"error": "Course not found or you don't have permission"}), 404

    # Lấy cards liên quan (nếu model Card có trường course_id)
    cards_data = []
    if hasattr(course, 'cards'): # Kiểm tra xem có relationship 'cards' không
        cards = Card.query.filter_by(course_id=course.id).all()
        cards_data = [card.to_dict() for card in cards]

    course_data = course.to_dict()
    course_data['cards'] = cards_data # Thêm danh sách cards vào response

    return jsonify(course_data)

# Cập nhật khóa học
@courses_bp.route("/courses/<int:course_id>", methods=["PUT"])
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
        current_app.logger.error(f"Error updating course {course_id}: {str(e)}") # Log lỗi
        return jsonify({"error": "Database error while updating course", "details": str(e)}), 500

    return jsonify({"message": "Course updated successfully", "course": course.to_dict()})

# Xóa khóa học
@courses_bp.route("/courses/<int:course_id>", methods=["DELETE"])
@token_required
def delete_course(current_user, course_id):
    course = Course.query.filter_by(id=course_id, owner_id=current_user.id).first()

    if not course:
        return jsonify({"error": "Course not found or you don't have permission to delete"}), 404

    try:
        # Nếu có card liên quan, cần xử lý (ví dụ: xóa card hoặc đặt course_id của card thành null)
        # Ở đây ví dụ xóa luôn cards liên quan
        Card.query.filter_by(course_id=course.id).delete()

        db.session.delete(course)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting course {course_id}: {str(e)}") # Log lỗi
        return jsonify({"error": "Database error while deleting course", "details": str(e)}), 500

    return jsonify({"message": "Course deleted successfully"})


# === CARD ROUTES (liên quan đến một Course cụ thể) ===

# Thêm card mới vào một khóa học
@courses_bp.route("/courses/<int:course_id>/cards", methods=["POST"])
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
        current_app.logger.error(f"Error adding card to course {course_id}: {str(e)}") # Log lỗi
        return jsonify({"error": "Database error while adding card", "details": str(e)}), 500

    return jsonify({"message": "Card added successfully", "card": card.to_dict()}), 201

# Lấy tất cả card của một khóa học (Route này có thể trùng với get_course nếu bạn gộp dữ liệu)
@courses_bp.route("/courses/<int:course_id>/cards", methods=["GET"])
@token_required
def get_cards_for_course(current_user, course_id):
    course = Course.query.filter_by(id=course_id, owner_id=current_user.id).first()
    if not course:
        return jsonify({"error": "Course not found or you don't have permission"}), 404

    cards = Card.query.filter_by(course_id=course.id).all()
    return jsonify([card.to_dict() for card in cards])

# Lưu ý: Bạn có thể cần các route để cập nhật và xóa từng card riêng lẻ.
# Những route đó có thể nằm trong `cards_bp.py` và bảo vệ bằng `@token_required`
# và kiểm tra xem `current_user` có phải là `owner` của `course` mà `card` đó thuộc về không.

# Ví dụ cho việc thêm phương thức to_dict() vào model (trong app/models.py)
# class Course(db.Model):
#     # ... các cột khác ...
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "description": self.description,
#             "owner_id": self.owner_id,
#             "created_at": self.created_at.isoformat() if self.created_at else None
#             # Thêm các trường khác nếu cần
#         }

# class Card(db.Model):
#     # ... các cột khác ...
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "front": self.front,
#             "back": self.back,
#             "course_id": self.course_id,
#             "created_at": self.created_at.isoformat() if self.created_at else None
#             # Thêm các trường khác nếu cần
#         }