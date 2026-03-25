import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    deadline TEXT,
    priority TEXT,
    done INTEGER DEFAULT 0
)
""")

conn.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

conn.close()

print("База создана ✅")