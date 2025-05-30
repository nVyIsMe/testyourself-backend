import os
from dotenv import load_dotenv

load_dotenv()  # Tải biến môi trường từ file .env

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_dev_secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL") or \
        'mysql+pymysql://root:your_mysql_password@localhost/testyourself_db'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL") or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        # raise ValueError("DATABASE_URL không được đặt trong biến môi trường!")
        SQLALCHEMY_DATABASE_URI = "placeholder"  # hoặc gán tạm gì cũng được để tránh lỗi
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
