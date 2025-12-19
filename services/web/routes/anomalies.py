from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId

from database.mongo import get_log, get_total_logs
import requests
import os

ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://ml-service:5001")

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
    page = int(request.args.get("page", 1))
    offset = page - 1

    log = get_log(offset)
    if not log:
        return jsonify({
            "page": page,
            "total": get_total_logs(),
            "data": None
        })

    return jsonify({
        "page": page,
        "total": get_total_logs(),
        "data": format_log(log)
    })


@bp.route("/api/latest")
def latest():
    log = get_log(0)
    if not log:
        return jsonify({"data": None})

    return jsonify(format_log(log))
