import os, requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/match", methods=["POST"])
def match():
    if not API_KEY:
        return jsonify({"error": "API key não configurada no servidor."}), 500
    data = request.get_json()
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01"
        },
        json=data,
        timeout=30
    )
    return jsonify(resp.json()), resp.status_code

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
