from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_cors import CORS

from routes.anomalies import bp as anomalies_bp
from routes.stats import bp as stats_bp
from routes.stream import bp as stream_bp
from routes.settings import bp as settings_bp
from routes.auth import bp as auth_bp

# Serve templates + static assets correctly
app = Flask(__name__, template_folder="templates", static_folder="assets")
app.secret_key = "radar_secret_key_change_me_in_prod" # TODO: Use env var
CORS(app)

# Use ProxyFix to handle headers when behind a proxy (e.g. Render)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


# -------------------------
# AUTH HELPER
# -------------------------
def is_logged_in():
    return session.get("logged_in")

@app.context_processor
def inject_user():
    return dict(logged_in=is_logged_in())

# -------------------------
# UI ROUTES
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")





@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html")

@app.route("/forensics")
def forensics():
    if not is_logged_in():
        return redirect(url_for("auth.login"))
    return render_template("forensics.html")



# -------------------------
# API Blueprints
# -------------------------
app.register_blueprint(anomalies_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(stream_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(auth_bp)

# -------------------------
# 404 Page
# -------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
