from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def health():
    return jsonify({"status": "Embed Service Operational", "service": "radar-embed"})

@app.route("/embed", methods=["POST"])
def embed_stub():
    # Placeholder for actual embedding logic
    return jsonify({"vector": [0.1, 0.2, 0.3], "note": "Placeholder embedding"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
