# app/admin.py
from flask import Blueprint, jsonify, abort
from flask_login import current_user, login_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "ADMIN":
        abort(403)  # từ chối nếu không phải admin

    return jsonify({"message": "Chào mừng ADMIN! Đây là dashboard riêng."})
