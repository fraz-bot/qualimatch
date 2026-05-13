import os, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/data/qualis")
def qualis_data():
    path = os.path.join(BASE_DIR, "qualis_data.b64")
    with open(path, "r") as f:
        data = f.read()
    return Response(data, mimetype="text/plain",
                    headers={"Cache-Control": "public, max-age=86400"})

@app.route("/api/match", methods=["POST"])
def match():
    if not API_KEY:
        return jsonify({"error": "API key não configurada."}), 500
    body = request.get_json()
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01"
        },
        json=body,
        timeout=60
    )
    return jsonify(resp.json()), resp.status_code

@app.route("/health")
def health():
    # Verifica se os arquivos existem
    files = ["index.html", "qualis_data.b64"]
    status = {f: os.path.exists(os.path.join(BASE_DIR, f)) for f in files}
    return jsonify({"ok": True, "files": status, "base_dir": BASE_DIR})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
