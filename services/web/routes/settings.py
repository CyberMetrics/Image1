from flask import Blueprint, jsonify, request

bp = Blueprint("settings", __name__)

# In-memory store for now (or could be DB)
CURRENT_THRESHOLD = 0.0025

@bp.route("/api/settings/threshold", methods=["GET"])
def get_threshold():
    return jsonify({"threshold": CURRENT_THRESHOLD})

@bp.route("/api/settings/threshold", methods=["POST"])
def set_threshold():
    global CURRENT_THRESHOLD
    data = request.json
    val = data.get("threshold")
    if val is not None:
        CURRENT_THRESHOLD = float(val)
    return jsonify({"threshold": CURRENT_THRESHOLD})
