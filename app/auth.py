from flask import Blueprint, redirect, session, request, jsonify
from app.models import db, User
from app.utils.oauth import get_google_flow
from flask_login import login_user, logout_user
import google.auth.transport.requests
import requests

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login/google")
def login_google():
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session["oauth_state"] = state
    return redirect(authorization_url)

@auth_bp.route("/callback")
def callback():
    flow = get_google_flow()

    # Restore the state to prevent CSRF attacks
    flow.fetch_token(
        authorization_response=request.url
    )

    credentials = flow.credentials
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    # Fetch user info from Google
    response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    user_info = response.json()

    # Find or create user in the database
    user = User.query.filter_by(email=user_info["email"]).first()
    if not user:
        user = User(
            email=user_info["email"],
            name=user_info.get("name"),
            profile_pic=user_info.get("picture")
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    # Redirect to dashboard after successful login
    return redirect("http://localhost:5173/dashboard")

@auth_bp.route("/logout")
def logout():
    session.clear()
    logout_user()
    return jsonify({"message": "Logged out"}), 200
