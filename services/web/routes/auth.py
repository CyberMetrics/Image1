from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import hashlib
from database.mongo import db

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("username")
        password = request.form.get("password")
        
        users_col = db["Users"]
        user = users_col.find_one({"email": email})
        
        if user:
            # Check password hash (SHA256)
            phash = hashlib.sha256(password.encode()).hexdigest()
            if user.get("password_hash") == phash:
                session["logged_in"] = True
                session["user"] = email
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials", "error")
        else:
            flash("User not found", "error")
            
    return render_template("login.html")

@bp.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not email or not password:
        flash("Email and Password required", "error")
        return redirect(url_for("auth.login"))
        
    users_col = db["Users"]
    if users_col.find_one({"email": email}):
        flash("User already exists", "error")
        return redirect(url_for("auth.login"))
        
    phash = hashlib.sha256(password.encode()).hexdigest()
    users_col.insert_one({
        "name": name,
        "email": email,
        "password_hash": phash,
        "created_at": "now" # simple timestamp, ideally use datetime
    })
    
    flash("Account created! Please log in.", "success")
    return redirect(url_for("auth.login"))

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# -------------------------
# OAUTH ROUTES
# -------------------------
import requests
from config.oauth_keys import *

# --- GITHUB ---
@bp.route("/login/github")
def github_login():
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        flash("GitHub OAuth not configured.", "error")
        return redirect(url_for("auth.login"))
        
    return redirect(f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=user:email")

@bp.route("/login/github/callback")
def github_callback():
    code = request.args.get("code")
    if not code:
        flash("Failed to log in with GitHub.", "error")
        return redirect(url_for("auth.login"))

    try:
        # 1. Exchange code for token
        token_response = requests.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        
        if not access_token:
            flash("Failed to retrieve access token from GitHub.", "error")
            return redirect(url_for("auth.login"))

        # 2. Get User Info
        user_response = requests.get(
            GITHUB_USER_API,
            headers={"Authorization": f"token {access_token}"},
        )
        user_info = user_response.json()
        
        # 3. Get Email (if private)
        user_email = user_info.get("email")
        if not user_email:
            email_response = requests.get(
                GITHUB_USER_EMAIL_API,
                headers={"Authorization": f"token {access_token}"},
            )
            emails = email_response.json()
            # Find primary verified email
            for e in emails:
                if e["primary"] and e["verified"]:
                    user_email = e["email"]
                    break
        
        if not user_email:
             flash("No verified email found for GitHub account.", "error")
             return redirect(url_for("auth.login"))

        users_name = user_info.get("name") or user_info.get("login")
        unique_id = str(user_info.get("id"))

        # Login or Create User
        users_col = db["Users"]
        user = users_col.find_one({"email": user_email})
        
        if not user:
            users_col.insert_one({
                "name": users_name,
                "email": user_email,
                "oauth_provider": "github",
                "oauth_id": unique_id,
                "created_at": "now"
            })
        
        session["logged_in"] = True
        session["user"] = user_email
        return redirect(url_for("dashboard"))

    except Exception as e:
        flash(f"GitHub Login failed: {str(e)}", "error")
        return redirect(url_for("auth.login"))

