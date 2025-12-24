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
        # Short timeout and broad exception catch to prevent 500s
        resp = requests.post(f"{ML_SERVICE_URL}/score", json={"log": doc}, timeout=0.5)
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
    from flask import request, session, Response
    from database.mongo import db, collection, find_user_collection
    import json
    import time
    
    view = request.args.get("view", "public")
    base_query = {}
    target_col = collection

    if view == "private":
        user = session.get("user")
        if user:
            found_col = find_user_collection(user)
            if found_col:
                target_col = db[found_col]
            else:
                target_col = None # User has no collection yet
        else:
            target_col = None # Not logged in but requested private

    def event_stream():
        # If no target collection (e.g. private view but no user data), 
        # just yield keep-alives.
        if target_col is None:
            while True:
                yield ": no data\n\n"
                time.sleep(5)
        
        last_id = None
        # BACKLOG REPLAY: Start from 100 records ago
        try:
            past_cursor = target_col.find(base_query).sort("_id", -1).skip(100).limit(1)
            past_docs = list(past_cursor)
            if past_docs:
                last_id = past_docs[0]["_id"]
        except Exception:
            last_id = None

        while True:
            try:
                query = {}
                if last_id:
                    query["_id"] = {"$gt": last_id}
                    cursor = target_col.find(query).sort("_id", 1).limit(1)
                else:
                    cursor = target_col.find(base_query).sort("_id", 1).limit(1)
                
                docs = list(cursor)
                for d in docs:
                    if str(d.get("_id")) == str(last_id): continue
                    
                    payload = format_log_sse(d)
                    yield f"data: {json.dumps(payload, default=str)}\n\n"
                    last_id = d.get("_id")
                
                time.sleep(1.0)
            except GeneratorExit:
                break
            except Exception as e:
                print(f"Stream Error: {e}")
                time.sleep(1.0)

    return Response(event_stream(), mimetype="text/event-stream")
