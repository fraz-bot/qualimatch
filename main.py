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
    with open(os.path.join(BASE_DIR, "qualis_data.b64"), "r") as f:
        data = f.read()
    return Response(data, mimetype="text/plain",
                    headers={"Cache-Control": "public, max-age=86400"})

@app.route("/data/sjr")
def sjr_data():
    with open(os.path.join(BASE_DIR, "sjr_data.b64"), "r") as f:
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

@app.route("/api/refs")
def refs():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "query obrigatória"}), 400
    try:
        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": query[:300],
                "fields": "title,authors,year,abstract,externalIds,openAccessPdf,citationCount",
                "limit": 20
            },
            headers={"User-Agent": "QualisMatch/1.0"},
            timeout=15
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    files = ["index.html", "qualis_data.b64", "sjr_data.b64"]
    status = {f: os.path.exists(os.path.join(BASE_DIR, f)) for f in files}
    return jsonify({"ok": True, "files": status})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
