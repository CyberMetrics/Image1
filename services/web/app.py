from flask import Flask, render_template
from flask_cors import CORS

from routes.anomalies import bp as anomalies_bp
from routes.stats import bp as stats_bp
from routes.stream import bp as stream_bp
from routes.settings import bp as settings_bp

# Serve templates + static assets correctly
app = Flask(__name__, template_folder="templates", static_folder="assets")
CORS(app)

# -------------------------
# UI ROUTES
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/forensics")
def forensics():
    return render_template("forensics.html")

@app.route("/neural")
def neural():
    return render_template("neural.html")

# -------------------------
# API Blueprints
# -------------------------
app.register_blueprint(anomalies_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(stream_bp)
app.register_blueprint(settings_bp)

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
    app.run(host="0.0.0.0", port=5000, threaded=True)
