from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# подключение к базе
def get_db():
    path = os.path.join(os.getcwd(), "database.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

# умный приоритет
def smart_priority(deadline):
    today = datetime.now().date()
    d = datetime.strptime(deadline, "%Y-%m-%d").date()
    diff = (d - today).days

    if diff <= 1:
        return "High"
    elif diff <= 3:
        return "Medium"
    else:
        return "Low"

# РЕГИСТРАЦИЯ
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user:
            conn.close()
            return "❌ Логин уже занят"

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "❌ Неверный логин или пароль"

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ГЛАВНАЯ
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

# ДОБАВИТЬ
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        deadline = request.form["deadline"]

        priority = smart_priority(deadline)

        conn = get_db()
        conn.execute(
            "INSERT INTO tasks (title, deadline, priority) VALUES (?, ?, ?)",
            (title, deadline, priority)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_task.html")

# УДАЛИТЬ
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# DONE
@app.route("/done/<int:id>")
def done(id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)