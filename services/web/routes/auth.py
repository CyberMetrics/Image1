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
