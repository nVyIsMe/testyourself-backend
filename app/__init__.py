import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_cors import CORS # Giữ lại
from app.config import config
from flask_migrate import Migrate

# Khởi tạo db và migrate
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    # Nạp biến môi trường từ file .env
    load_dotenv()

    # Khởi tạo Flask app
    app = Flask(__name__)

    # ... (các dòng app.config của bạn ở đây) ...
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_jwt_secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DEV_DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["UPLOAD_FOLDER"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
    app.config.from_object(config['development'])

        # Lấy thư mục gốc của dự án (thư mục chứa 'app', 'run.py', 'uploads')
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # Tạo đường dẫn chính xác đến thư mục 'uploads' ở gốc
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "uploads")
    # *** ĐÂY LÀ DÒNG QUAN TRỌNG NHẤT ***
    # Cho phép frontend và các header cần thiết
    CORS(app, 
     origins=["http://localhost:5173"], 
     supports_credentials=True,
     allow_headers=["*"]  # DÙNG DẤU SAO CHO DỄ DEBUG NHẤT
)

    # *** ĐẢM BẢO KHÔNG CÓ @app.after_request NÀO Ở ĐÂY ***

    # Cho phép truy cập ảnh tĩnh trong thư mục uploads
    @app.route('/uploads/<filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Khởi tạo db và migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Đăng ký các blueprint
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.courses import courses_bp
    app.register_blueprint(courses_bp)

    from app.routes.public import public_bp
    app.register_blueprint(public_bp)
    
    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Log REDIRECT_URI nếu có dùng OAuth
    from app.utils.oauth import REDIRECT_URI
    app.logger.info(f"🔁 REDIRECT URI đang dùng: {REDIRECT_URI}")

    return app
