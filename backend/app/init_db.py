# backend/app/__init__.py
from flask import Flask
from .db import init_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "bytt-meg-senere"

    init_db()  # oppretter tabeller + admin-bruker hvis de mangler

    from .routes import bp
    app.register_blueprint(bp)

        # --- NYTT: utvid users med varselpreferanser (hvis kolonnene ikke finnes) ---
    try:
        cur.execute("ALTER TABLE users ADD COLUMN notify_email INTEGER NOT NULL DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("ALTER TABLE users ADD COLUMN notify_inapp INTEGER NOT NULL DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    # --- NYTT: vurderinger på saker ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            user TEXT NOT NULL,
            stars INTEGER NOT NULL,
            feedback TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY(ticket_id) REFERENCES tickets(id)
        )
    """)

    # --- NYTT: varsler i appen ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            message TEXT NOT NULL,
            link TEXT,
            read INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # --- NYTT: kunnskapsbaseartikler ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT
        )
    """)

    # --- NYTT: aktivitetslogg ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    return app


