from flask import Blueprint, jsonify
from database.mongo import collection as COLL
import requests
import os

ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://ml-service:5001")

bp = Blueprint("stats", __name__)

@bp.route("/api/stats")
def stats():
    try:
        total = COLL.count_documents({})
    except Exception:
        total = 0

    # Lightweight session max: compute across recent N documents (to avoid scanning full DB)
    session_max = 0.0
    try:
        # Lower limit to 50 for performance since we are making HTTP requests
        recent = list(COLL.find().sort("_id", -1).limit(50))
        for d in recent:
            try:
                # score = float(compute_score(d))
                resp = requests.post(f"{ML_SERVICE_URL}/score", json={"log": d}, timeout=1)
                if resp.status_code == 200:
                    score = float(resp.json().get("score", 0.0))
                else:
                    score = 0.0
                    
                if score > session_max:
                    session_max = score
            except Exception:
                continue
    except Exception:
        session_max = 0.0

    return jsonify({
        "db_total": total,
        "session_max": session_max
    })
