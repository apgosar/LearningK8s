import os
import time
from urllib.parse import quote_plus

import psycopg2
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from psycopg2.extras import RealDictCursor


def database_url():
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "appdb")
    user = os.getenv("DB_USER", "appuser")
    password = os.getenv("DB_PASSWORD", "apppassword")

    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{quote_plus(name)}"
    )


def get_connection():
    return psycopg2.connect(database_url(), connect_timeout=3)


def ensure_schema(retries=30, delay=2):
    sql = """
    CREATE TABLE IF NOT EXISTS messages (
      id SERIAL PRIMARY KEY,
      author VARCHAR(60) NOT NULL,
      body TEXT NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    last_error = None
    for _ in range(retries):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
            return
        except psycopg2.Error as exc:
            last_error = exc
            time.sleep(delay)

    raise RuntimeError("Database schema could not be initialized") from last_error


def list_messages():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, author, body, created_at
                FROM messages
                ORDER BY created_at DESC
                LIMIT 30;
                """
            )
            return cur.fetchall()


def create_message(author, body):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (author, body) VALUES (%s, %s);",
                (author, body),
            )


def delete_message(message_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM messages WHERE id = %s;", (message_id,))


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "change-me-for-real-use")


@app.get("/")
def index():
    db_error = None
    messages = []

    try:
        messages = list_messages()
    except psycopg2.Error:
        app.logger.exception("Could not fetch messages")
        db_error = "Database is not available yet."

    return render_template("index.html", messages=messages, db_error=db_error)


@app.post("/messages")
def add_message():
    author = request.form.get("author", "").strip()[:60]
    body = request.form.get("body", "").strip()[:500]

    if not author or not body:
        flash("Name and message are required.")
        return redirect(url_for("index"))

    try:
        create_message(author, body)
        flash("Message saved.")
    except psycopg2.Error:
        app.logger.exception("Could not save message")
        flash("Message could not be saved because the database is unavailable.")

    return redirect(url_for("index"))


@app.post("/messages/<int:message_id>/delete")
def remove_message(message_id):
    try:
        delete_message(message_id)
        flash("Message deleted.")
    except psycopg2.Error:
        app.logger.exception("Could not delete message")
        flash("Message could not be deleted because the database is unavailable.")

    return redirect(url_for("index"))


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/readyz")
def readyz():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return jsonify(status="ready")
    except psycopg2.Error:
        return jsonify(status="not-ready"), 503


ensure_schema()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

