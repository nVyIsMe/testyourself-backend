from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")  # Ensure this is set up in your config

    # Initialize the extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Set up CORS (allow requests from your React frontend)
    CORS(app, origins="http://localhost:5173")  # Adjust this to your frontend's URL if needed

    # Register Blueprints
    from app.auth import auth_bp  # Import auth blueprint here
    app.register_blueprint(auth_bp)  # No need for '/api' prefix, it's in the blueprint

    from app.routes.decks import decks_bp
    app.register_blueprint(decks_bp, url_prefix="/api")  # Register decks blueprint with '/api' prefix

    return app
