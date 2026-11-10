from flask import Flask, jsonify, send_from_directory
from pathlib import Path
from database import init_db

app = Flask(__name__)

@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "BOT SYRIA",
        "server": "termux"
    })

@app.get("/")
def home():
    return send_from_directory(
        Path(__file__).with_name("web"),
        "index.html"
    )


if __name__ == "__main__":
    init_db()
    print("🚀 BOT SYRIA SERVER يعمل على http://127.0.0.1:8080")
    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False,
        threaded=True
    )
