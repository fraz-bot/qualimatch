import os, requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/data/qualis")
def qualis_data():
    return send_from_directory(BASE_DIR, "qualis_data.b64", mimetype="text/plain",
                               max_age=86400)  # cache 24h no browser

@app.route("/api/match", methods=["POST"])
def match():
    if not API_KEY:
        return jsonify({"error": "API key não configurada."}), 500
    data = request.get_json()
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01"
        },
        json=data,
        timeout=60
    )
    return jsonify(resp.json()), resp.status_code

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
