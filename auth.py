import sqlite3
import bcrypt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "users.db")

conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    email TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")
conn.commit()

def create_user(email, password, role):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (email, hashed_pw, role))
    conn.commit()

def login_user(email, password):
    c.execute("SELECT password, role FROM users WHERE email=?", (email,))
    result = c.fetchone()
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return result[1]
    return None