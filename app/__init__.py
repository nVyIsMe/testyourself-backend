from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    CORS(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.decks import decks_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(decks_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    return app
