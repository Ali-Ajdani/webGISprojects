import sqlite3

DB_NAME = "app.db"

def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE NOT NULL,
        Password TEXT NOT NULL
    );
    """)

    # Add a test user if not exists
    cur.execute("SELECT 1 FROM Users WHERE Username = ?", ("ali",))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO Users (Username, Password) VALUES (?, ?)",
            ("ali", "123456")
        )

    con.commit()
    con.close()
