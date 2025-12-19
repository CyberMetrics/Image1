from flask import Blueprint, Response
import time
from bson.objectid import ObjectId
from database.mongo import collection as COLL
import json
import requests
import os

ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://ml-service:5001")
if not ML_SERVICE_URL.startswith("http"):
    ML_SERVICE_URL = f"http://{ML_SERVICE_URL}"

bp = Blueprint("stream", __name__)

def format_log_sse(doc):
    # keep the same format as anomalies.format_log but compact
    # score = compute_score(doc)
    try:
        resp = requests.post(f"{ML_SERVICE_URL}/score", json={"log": doc}, timeout=1)
        if resp.status_code == 200:
            score = resp.json().get("score", 0.0)
        else:
            score = 0.0
    except Exception:
        score = 0.0
    if score < 0.010:
        sev = "Safe"
    elif score < 0.020:
        sev = "Low"
    elif score < 0.050:
        sev = "Medium"
    else:
        sev = "High"

    return {
        "id": str(doc.get("_id")),
        "timestamp": doc.get("timestamp"),
        "asset_id": f"{doc.get('hostname', 'UNKNOWN').upper()}_NODE",
        "protocol": "SYS",
        "service": doc.get("source", "Unknown"),
        "score": score,
        "severity": sev,
        "raw_data": doc.get("message", ""),
        "is_anomaly": score >= 0.050
    }

@bp.route("/api/stream/logs")
def stream_logs():
    def event_stream():
        last_id = None
        # initialize last_id = most recent doc's _id (if any)
        try:
            last_doc = COLL.find_one(sort=[("_id", -1)])
            if last_doc:
                last_id = last_doc.get("_id")
        except Exception:
            last_id = None

        while True:
            try:
                # find docs with _id > last_id
                if last_id:
                    cursor = COLL.find({"_id": {"$gt": last_id}}).sort("_id", 1)
                else:
                    cursor = COLL.find().sort("_id", -1).limit(1)
                docs = list(cursor)
                for d in docs:
                    payload = format_log_sse(d)
                    yield f"data: {json.dumps(payload, default=str)}\n\n"
                    last_id = d.get("_id")
                time.sleep(1.0)
            except GeneratorExit:
                break
            except Exception:
                # on any error, wait briefly and continue
                time.sleep(1.0)
                continue

    return Response(event_stream(), mimetype="text/event-stream")
