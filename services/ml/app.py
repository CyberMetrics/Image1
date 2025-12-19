from flask import Flask, request, jsonify
from ml.model_loader import compute_score

app = Flask(__name__)

@app.route("/score", methods=["POST"])
def score():
    data = request.json
    log = data.get("log")
    if not log:
        return jsonify({"error": "No log provided"}), 400
    
    try:
        score = compute_score(log)
        return jsonify({"score": score})
    except Exception as e:
        app.logger.error(f"Error computing score: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run on port 5001 to distinguish from Web Service (5000)
    app.run(host="0.0.0.0", port=5001)
