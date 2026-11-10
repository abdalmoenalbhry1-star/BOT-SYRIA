from flask import Flask, jsonify
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
    return jsonify({
        "name": "BOT SYRIA",
        "status": "online"
    })


if __name__ == "__main__":
    init_db()
    print("🚀 BOT SYRIA SERVER يعمل على http://127.0.0.1:8080")
    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False,
        threaded=True
    )
