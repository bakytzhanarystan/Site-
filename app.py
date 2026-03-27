from flask import Flask, render_template, request, jsonify, session, redirect
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

GEMINI_API_KEY = "AIzaSyAdk5uE65eIu9tn-CklPOmkOgUlJbf6bAY"

# ---------------- БД ----------------
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    # задачи
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        deadline TEXT,
        priority TEXT,
        completed INTEGER DEFAULT 0
    )
    """)

    # пользователи
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- AUTH ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form

        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        user = cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (data["username"], data["password"])
        ).fetchone()

        conn.close()

        if user:
            session["user"] = data["username"]
            return redirect("/")
        else:
            return "❌ Неверный логин"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form

        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        exists = cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (data["username"],)
        ).fetchone()

        if exists:
            conn.close()
            return "❌ Логин занят"

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (data["username"], data["password"])
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------- MAIN ----------------

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

# ---------------- API ----------------

@app.route("/add_task", methods=["POST"])
def add_task():
    if "user" not in session:
        return jsonify({"error": "unauthorized"})

    data = request.json
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (text, deadline, priority) VALUES (?, ?, ?)",
        (data["text"], data["deadline"], data["priority"])
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


@app.route("/tasks")
def tasks():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "text": r[1],
            "deadline": r[2],
            "priority": r[3],
            "completed": bool(r[4])
        })

    return jsonify(result)


@app.route("/delete_task/<int:id>", methods=["DELETE"])
def delete_task(id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/toggle_complete/<int:id>", methods=["POST"])
def toggle_complete(id):
    data = request.json

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET completed=? WHERE id=?",
        (int(data["completed"]), id)
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# ---------------- AI ----------------

@app.route("/ai", methods=["POST"])
def ai():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("SELECT text, deadline, priority FROM tasks WHERE completed = 0")
    tasks = cursor.fetchall()
    conn.close()

    if not tasks:
        return jsonify({"recommendation": "Все задачи выполнены 🎉"})

    prompt = "Проанализируй задачи студента:\n"

    for t in tasks:
        prompt += f"{t[0]} | дедлайн: {t[1]} | приоритет: {t[2]}\n"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(url, json=payload)
    result = response.json()

    text = result["candidates"][0]["content"]["parts"][0]["text"]

    return jsonify({"recommendation": text})


if __name__ == "__main__":
    app.run(debug=True)