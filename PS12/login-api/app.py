from fastapi import FastAPI, HTTPException, Query
import sqlite3
from db import init_db, DB_NAME

app = FastAPI(title="Login API (No ORM)")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/login")
def login(
    username: str = Query(...),
    password: str = Query(...)
):
    try:
        con = sqlite3.connect(DB_NAME, check_same_thread=False)
        cur = con.cursor()

        cur.execute(
            "SELECT Id FROM Users WHERE Username=? AND Password=?",
            (username, password)
        )
        row = cur.fetchone()
    finally:
        con.close()

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "ok": True,
        "userId": row[0]
    }
