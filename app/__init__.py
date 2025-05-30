from flask import Flask, jsonify, request # << THÊM request VÀO ĐÂY
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager # Bạn đang dùng JWTManager nhưng decorator token_required là custom
from flask_cors import CORS
from flask_login import LoginManager
import logging # << THÊM import logging

from .config import config

# --- Khởi tạo extensions ---
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager() # Flask-JWT-Extended
cors = CORS()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)

    # --- Load config ---
    if config_name not in config:
        raise ValueError(f"Cấu hình '{config_name}' không tồn tại.")
    app.config.from_object(config[config_name])
    if hasattr(config[config_name], 'init_app'):
        config[config_name].init_app(app)

    # --- Cấu hình Logging cơ bản (NẾU CHƯA CÓ Ở CHỖ KHÁC) ---
    # Điều này quan trọng để app.logger hoạt động nếu bạn không chạy ở debug mode
    if not app.debug or logging.getLogger('werkzeug').level == logging.INFO: # Tránh log trùng khi debug mode reload
        stream_handler = logging.StreamHandler()
        # Đặt mức log DEBUG để thấy tất cả, hoặc INFO cho production
        stream_handler.setLevel(logging.DEBUG if app.config.get("DEBUG") else logging.INFO) 
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]')
        stream_handler.setFormatter(formatter)
        
        # Xóa handler mặc định của Flask (nếu có) để tránh log trùng khi DEBUG=True
        # và thêm handler của chúng ta
        if app.logger.hasHandlers():
            app.logger.handlers.clear()
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.DEBUG if app.config.get("DEBUG") else logging.INFO)
        app.logger.info('Flask App initialized and custom logging configured.')


    # --- Init extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app) # Khởi tạo Flask-JWT-Extended
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    login_manager.init_app(app)


    # --- LOG REQUEST ĐẾN ---
    @app.before_request
    def log_request_info_detailed(): # Đổi tên hàm để tránh trùng nếu bạn có hàm khác
        # Sử dụng app.logger đã được cấu hình
        app.logger.debug("--- INCOMING REQUEST (app.before_request) ---")
        app.logger.debug(f"Path: {request.path}")
        app.logger.debug(f"Method: {request.method}")
        app.logger.debug("Headers:")
        for header, value in request.headers.items():
            app.logger.debug(f"  {header}: {value}")
        # In đậm hoặc làm nổi bật header Authorization nếu có
        if 'Authorization' in request.headers:
            app.logger.debug(f"  **Authorization Header (Direct Access): {request.headers.get('Authorization')}**")
        else:
            app.logger.warning("  **Authorization Header: NOT FOUND in request.headers by Flask**")
        app.logger.debug("--- END INCOMING REQUEST (app.before_request) ---")


    # --- Flask-Login: Load user (Nếu bạn vẫn dùng Flask-Login cho một số phần) ---
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User # Di chuyển import vào trong để tránh circular import
        return User.query.get(int(user_id))

    # --- Import Blueprints ---
    from .auth import auth_bp
    from .admin import admin_bp
    from .routes.courses import courses_bp
    from .routes.cards import cards_bp
    from .routes.favorites import favorites_bp
    from .routes.history import history_bp

    # --- Đăng ký Blueprints ---
    # Thứ tự đăng ký blueprint thường không quá quan trọng,
    # trừ khi có các before_request handler cụ thể cho từng blueprint.
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(courses_bp, url_prefix='/api') # /api/courses sẽ được xử lý bởi courses_bp
    app.register_blueprint(cards_bp, url_prefix='/api')   # /api/courses/:id/cards cũng có thể ở đây
    app.register_blueprint(favorites_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')

    # --- Xử lý lỗi 403: Forbidden ---
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Bạn không có quyền truy cập"}), 403

    return app