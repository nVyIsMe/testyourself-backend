import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS

# Khởi tạo db
db = SQLAlchemy()

def create_app(config_name=None):
    load_dotenv()

    app = Flask(__name__)

    # Cấu hình ứng dụng
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_jwt_secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DEV_DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_SECURE"] = False

    # Khởi tạo DB
    db.init_app(app)

    # Cấu hình CORS cho phép frontend từ localhost:5173
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True, 
         allow_headers=["Content-Type", "Authorization"], 
         allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Xử lý OPTIONS request (preflight request)
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response

    # Import và đăng ký blueprint
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.courses import courses_bp
    app.register_blueprint(courses_bp)

    # Import REDIRECT_URI để ghi log
    from app.utils.oauth import REDIRECT_URI
    app.logger.info(f"🔁 REDIRECT URI đang dùng: {REDIRECT_URI}")

    return app
