import sqlite3
from typing import List, Dict, Any, Optional

# ... resten av db.py (inkl. _conn()) ...


def init_db() -> None:
    conn = _conn()
    cur = conn.cursor()

    # ... eksisterende CREATE TABLE users/tickets osv. ...

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
            cover_url TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT
        )
    """)

    # Migration: Legg til cover_url hvis kolonne mangler
    try:
        cur.execute("ALTER TABLE articles ADD COLUMN cover_url TEXT")
    except sqlite3.OperationalError:
        pass

    # --- NYTT: aktivitetslogg ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # --- NYTT: attachments (vedlegg til tickets) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            stored_filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            uploaded_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY(ticket_id) REFERENCES tickets(id)
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# ATTACHMENTS
# -----------------------------
def add_attachment(ticket_id: int, stored_filename: str, original_filename: str, uploaded_by: str) -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO attachments (ticket_id, stored_filename, original_filename, uploaded_by)
        VALUES (?, ?, ?, ?)
        """,
        (int(ticket_id), stored_filename, original_filename, uploaded_by),
    )
    conn.commit()
    attachment_id = int(cur.lastrowid)
    conn.close()
    return attachment_id


def get_attachments(ticket_id: int) -> List[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, ticket_id, stored_filename, original_filename, uploaded_by, uploaded_at
        FROM attachments
        WHERE ticket_id = ?
        ORDER BY id DESC
        """,
        (int(ticket_id),),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_attachment(attachment_id: int) -> Optional[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, ticket_id, stored_filename, original_filename, uploaded_by, uploaded_at
        FROM attachments
        WHERE id = ?
        """,
        (int(attachment_id),),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


