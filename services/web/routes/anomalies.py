from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId

from database.mongo import get_log, get_total_logs
import requests
import os

ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://ml-service:5001")
if not ML_SERVICE_URL.startswith("http"):
    ML_SERVICE_URL = f"http://{ML_SERVICE_URL}"

bp = Blueprint("anomalies", __name__)


def format_log(log):
    """ Convert Mongo log → UI anomaly format """

    # score = compute_score(log)
    try:
        resp = requests.post(f"{ML_SERVICE_URL}/score", json={"log": log}, timeout=2)
        if resp.status_code == 200:
            score = resp.json().get("score", 0.0)
        else:
            score = 0.0 # Default fallback
    except Exception:
         score = 0.0

    # severity mapping
    if score < 0.010:
        sev = "Safe"
    elif score < 0.020:
        sev = "Low"
    elif score < 0.050:
        sev = "Medium"
    else:
        sev = "High"

    return {
        "id": str(log.get("_id", "")),
        "timestamp": log.get("timestamp", ""),
        "asset_id": f"{log.get('hostname', 'UNKNOWN').upper()}_NODE",
        "protocol": "SYS",
        "service": log.get("source", "Unknown"),
        "score": score,
        "severity": sev,
        "raw_data": log.get("message", ""),
        "is_anomaly": score >= 0.050
    }


@bp.route("/api/anomalies")
def anomalies():
    from flask import session
    from database.mongo import db, collection, find_user_collection, get_logs
    from datetime import datetime, timedelta

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 1)) # Default 1 if not specified (legacy)
    view = request.args.get("view", "public")
    rng = request.args.get("range", "")
    start_str = request.args.get("start", "")
    end_str = request.args.get("end", "")

    offset = (page - 1) * per_page
    
    target_col = collection
    if view == "private":
        user = session.get("user")
        if user:
            found_col = find_user_collection(user)
            if found_col:
                target_col = db[found_col]
            else:
                 return jsonify({"page": page, "total": 0, "data": []})
        else:
            return jsonify({"page": page, "total": 0, "data": []})

    # Build Query
    query = {}
    if rng == 'day':
        query['timestamp'] = {'$gte': (datetime.utcnow() - timedelta(hours=24)).isoformat()}
    elif rng == 'week':
        query['timestamp'] = {'$gte': (datetime.utcnow() - timedelta(days=7)).isoformat()}
    elif start_str and end_str:
        query['timestamp'] = {'$gte': start_str, '$lte': end_str}

    # Fetch
    logs = get_logs(skip=offset, limit=per_page, target_col=target_col, query=query)
    total = get_total_logs(target_col=target_col) # Approx total (filtered total is expensive, this is confusing but standard for now)

    # Format
    data = [format_log(l) for l in logs]

    # Return
    return jsonify({
        "page": page,
        "total": total,
        "data": data # Always list
    })


@bp.route("/api/latest")
def latest():
    from flask import session
    from database.mongo import db, collection, find_user_collection
    
    view = request.args.get("view", "public")
    target_col = collection
    
    if view == "private":
        user = session.get("user")
        if user:
            found_col = find_user_collection(user)
            if found_col:
                target_col = db[found_col]
            else:
                return jsonify({"data": None})
        else:
            return jsonify({"data": None})

    log = get_log(0, target_col=target_col)
    if not log:
        return jsonify({"data": None})

    return jsonify(format_log(log))
