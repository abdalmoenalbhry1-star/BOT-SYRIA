from flask import Flask, jsonify, send_from_directory, request
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


@app.get("/api/tasks")
def get_tasks():
    from database import get_connection

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, title, description, link, reward, seats, status, created_at
            FROM tasks
            WHERE status = 'active' AND seats > 0
            ORDER BY id DESC
        """).fetchall()

    return jsonify({
        "status": "ok",
        "tasks": [dict(row) for row in rows]
    })


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id):
    from database import get_connection

    with get_connection() as conn:
        row = conn.execute("""
            SELECT id, title, description, link, reward, seats, status, created_at
            FROM tasks
            WHERE id = ?
        """, (task_id,)).fetchone()

    if row is None:
        return jsonify({
            "status": "error",
            "message": "Task not found"
        }), 404

    return jsonify({
        "status": "ok",
        "task": dict(row)
    })

@app.get("/admin")
def admin_page():
    return send_from_directory(
        Path(__file__).with_name("web") / "admin",
        "index.html"
    )


@app.post("/api/admin/tasks")
def admin_add_task():
    from database import get_connection

    data = request.get_json(silent=True) or {}

    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    link = str(data.get("link", "")).strip()

    try:
        reward = int(data.get("reward", 0))
        seats = int(data.get("seats", 0))
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "المكافأة والمقاعد يجب أن تكون أرقاماً."
        }), 400

    if not title or reward <= 0 or seats <= 0:
        return jsonify({
            "status": "error",
            "message": "العنوان والمكافأة والمقاعد مطلوبة."
        }), 400

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO tasks
            (title, description, link, reward, seats, status)
            VALUES (?, ?, ?, ?, ?, 'active')
        """, (title, description, link, reward, seats))

        task_id = cursor.lastrowid
        conn.commit()

    return jsonify({
        "status": "ok",
        "message": "تمت إضافة المهمة بنجاح.",
        "task_id": task_id
    }), 201

if __name__ == "__main__":
    init_db()
    print("🚀 BOT SYRIA SERVER يعمل على http://127.0.0.1:8080")
    app.run(
        host="0.0.0.0",
        port=int(__import__("os").environ.get("PORT", "8080")),
        debug=False,
        threaded=True
    )
