from flask import Blueprint, jsonify
from database.mongo import collection as COLL
import requests
import os

ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://ml-service:5001")
if not ML_SERVICE_URL.startswith("http"):
    ML_SERVICE_URL = f"http://{ML_SERVICE_URL}"

bp = Blueprint("stats", __name__)

@bp.route("/api/stats")
def stats():
    from flask import request, session
    from database.mongo import collection, db, find_user_collection
    
    view = request.args.get("view", "public")
    target_col = collection
    
    if view == "private":
        user = session.get("user")
        if user:
            found_col = find_user_collection(user)
            if found_col:
                target_col = db[found_col]
            else:
                target_col = None
        else:
            target_col = None

    if target_col is None:
        return jsonify({"db_total": 0, "session_max": 0.0})

    try:
        total = target_col.count_documents({})
    except Exception:
        total = 0

    # Lightweight session max: compute across recent N documents
    session_max = 0.0
    try:
        # Lower limit to 50 for performance since we are making HTTP requests
        recent = list(target_col.find().sort("_id", -1).limit(50))
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
