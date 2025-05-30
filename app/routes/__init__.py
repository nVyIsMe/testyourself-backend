from flask import Blueprint

# Đây là blueprint tổng để nhóm các route lại (nếu cần)
routes_bp = Blueprint("routes", __name__)

# Blueprint con từ từng module
from app.routes.courses import courses_bp
from app.routes.cards import cards_bp
from app.routes.favorites import favorites_bp
from app.routes.history import history_bp
from app.routes.admin import admin_bp

# Hàm gọi để đăng ký tất cả route vào app chính
def register_routes(app):
    app.register_blueprint(courses_bp, url_prefix="/api")
    app.register_blueprint(cards_bp, url_prefix="/api")
    app.register_blueprint(favorites_bp, url_prefix="/api")
    app.register_blueprint(history_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
