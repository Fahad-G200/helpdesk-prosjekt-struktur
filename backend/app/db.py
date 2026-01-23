from __future__ import annotations

import os
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from werkzeug.security import generate_password_hash
from .config import Config

logger = logging.getLogger(__name__)

DB_PATH = Path(Config.DATABASE_PATH)


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _conn()
    cur = conn.cursor()

    # USERS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            pw_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            email TEXT,
            phone TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_login TEXT,
            notify_email INTEGER NOT NULL DEFAULT 1,
            notify_inapp INTEGER NOT NULL DEFAULT 1,
            notify_sms INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Hvis DB allerede finnes fra før (uten nye kolonner), legg til kolonnene trygt:
    for stmt in [
        "ALTER TABLE users ADD COLUMN email TEXT",
        "ALTER TABLE users ADD COLUMN phone TEXT",
        "ALTER TABLE users ADD COLUMN notify_email INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE users ADD COLUMN notify_inapp INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE users ADD COLUMN notify_sms INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE users ADD COLUMN last_login TEXT",
    ]:
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass

    # TICKETS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            desc TEXT NOT NULL,
            owner TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Annet',
            priority TEXT NOT NULL DEFAULT 'Middels',
            device TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Åpen',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            closed_at TEXT
        )
    """)

    # NOTIFICATIONS (in-app)
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

    # RATINGS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL UNIQUE,
            user TEXT NOT NULL,
            stars INTEGER NOT NULL,
            feedback TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY(ticket_id) REFERENCES tickets(id)
        )
    """)

    # KNOWLEDGE BASE ARTICLES
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

    # ACTIVITY LOG
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ATTACHMENTS (vedlegg til tickets)
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

    # Opprett admin/support uten hardkodet passord
    cur.execute("SELECT 1 FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        admin_pw = os.environ.get("ADMIN_PASSWORD")
        if not admin_pw:
            logger.warning("ADMIN_PASSWORD ikke satt. Admin-bruker ble ikke opprettet.")
        else:
            cur.execute(
                "INSERT INTO users (username, pw_hash, role) VALUES (?, ?, ?)",
                ("admin", generate_password_hash(admin_pw, method="pbkdf2:sha256"), "support"),
            )
            logger.info("Admin/support bruker opprettet (admin).")

    conn.commit()
    conn.close()


# -----------------------------
# USERS
# -----------------------------
def user_exists(username: str) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    ok = cur.fetchone() is not None
    conn.close()
    return ok


def create_user(
    username: str,
    pw_hash: str,
    role: str = "user",
    email: Optional[str] = None,
    phone: Optional[str] = None,
) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (username, pw_hash, role, email, phone)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, pw_hash, role, email, phone),
    )
    conn.commit()
    conn.close()


def get_user(username: str):
    conn = _conn()
    cur = conn.cursor()

    # Bakoverkompatibel: hvis DB-en er laget før preferansekolonner ble lagt til,
    # kan SELECT feile. Da faller vi tilbake og setter default-verdier.
    try:
        cur.execute(
            "SELECT username, pw_hash, role, email, notify_email, notify_inapp, last_login "
            "FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    except sqlite3.OperationalError:
        cur.execute(
            "SELECT username, pw_hash, role, email, last_login FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        d["notify_email"] = 1
        d["notify_inapp"] = 1
        return d


def update_last_login(username: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_login = datetime('now') WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def update_preferences(
    username: str,
    notify_email: int,
    notify_inapp: int,
    notify_sms: int = 0,
    phone: Optional[str] = None,
) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE users
        SET notify_email = ?,
            notify_inapp = ?,
            notify_sms = ?,
            phone = ?
        WHERE username = ?
        """,
        (int(notify_email), int(notify_inapp), int(notify_sms), phone, username),
    )
    conn.commit()
    conn.close()


def get_support_users() -> List[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT username, email, phone, notify_email, notify_inapp, notify_sms
        FROM users
        WHERE role = 'support'
        ORDER BY username ASC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# -----------------------------
# TICKETS
# -----------------------------
def add_ticket(owner: str, title: str, desc: str, category: str, priority: str, device: str) -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tickets (title, desc, owner, category, priority, device, status, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Åpen', datetime('now'))
        """,
        (title.strip(), desc.strip(), owner, category, priority, device),
    )
    conn.commit()
    ticket_id = int(cur.lastrowid)
    conn.close()
    return ticket_id


def get_tickets(owner: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    if owner is None:
        cur.execute("""
            SELECT t.*, r.stars AS rating, r.feedback AS feedback
            FROM tickets t
            LEFT JOIN ratings r ON r.ticket_id = t.id
            ORDER BY t.id DESC
        """)
    else:
        cur.execute("""
            SELECT t.*, r.stars AS rating, r.feedback AS feedback
            FROM tickets t
            LEFT JOIN ratings r ON r.ticket_id = t.id
            WHERE t.owner = ?
            ORDER BY t.id DESC
        """, (owner,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.*, r.stars AS rating, r.feedback AS feedback
        FROM tickets t
        LEFT JOIN ratings r ON r.ticket_id = t.id
        WHERE t.id = ?
    """, (ticket_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def close_ticket(ticket_id: int) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE tickets
        SET status = 'Lukket',
            updated_at = datetime('now'),
            closed_at = datetime('now')
        WHERE id = ?
        """,
        (ticket_id,),
    )
    conn.commit()
    conn.close()


# -----------------------------
# RATINGS
# -----------------------------
def add_rating(ticket_id: int, user: str, stars: int, feedback: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ratings (ticket_id, user, stars, feedback) VALUES (?, ?, ?, ?)",
        (ticket_id, user, stars, feedback.strip()),
    )
    conn.commit()
    conn.close()


def get_rating(ticket_id: int) -> Optional[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT stars, feedback FROM ratings WHERE ticket_id = ? LIMIT 1", (ticket_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# -----------------------------
# NOTIFICATIONS (in-app)
# -----------------------------
def add_notification(user: str, message: str, link: Optional[str] = None) -> None:
    conn = _conn()
    cur = conn.cursor()

    cur.execute("SELECT notify_inapp FROM users WHERE username = ?", (user,))
    row = cur.fetchone()
    if not row or int(row["notify_inapp"]) != 1:
        conn.close()
        return

    cur.execute(
        "INSERT INTO notifications (user, message, link) VALUES (?, ?, ?)",
        (user, message, link),
    )
    conn.commit()
    conn.close()


def get_notifications(user: str) -> List[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications WHERE user = ? ORDER BY id DESC", (user,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_all_notifications_read(user: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET read = 1 WHERE user = ?", (user,))
    conn.commit()
    conn.close()


def count_notifications(user: str) -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM notifications WHERE user = ? AND read = 0", (user,))
    row = cur.fetchone()
    conn.close()
    return int(row["c"]) if row else 0


# -----------------------------
# KNOWLEDGE BASE
# -----------------------------
def create_article(title: str, content: str, author: str) -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO articles (title, content, author) VALUES (?, ?, ?)",
        (title.strip(), content.strip(), author),
    )
    conn.commit()
    article_id = int(cur.lastrowid)
    conn.close()
    return article_id


def get_articles() -> List[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, created_at FROM articles ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_article(article_id: int) -> Optional[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_article(article_id: int, title: str, content: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE articles SET title = ?, content = ?, updated_at = datetime('now') WHERE id = ?",
        (title.strip(), content.strip(), article_id),
    )
    conn.commit()
    conn.close()


def delete_article_db(article_id: int) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    conn.commit()
    conn.close()


# -----------------------------
# ACTIVITY LOG
# -----------------------------
def log_activity(user: str, details: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO activity (user, details) VALUES (?, ?)",
        (user, details),
    )
    conn.commit()
    conn.close()


def get_activity(limit: int = 100) -> List[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activity ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


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

# -----------------------------
# ADMIN: Users & Tickets helpers
# -----------------------------

def get_all_users() -> List[Dict[str, Any]]:
    """Get all users for admin management"""
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT username, role, email, created_at, last_login
        FROM users
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def change_user_role(username: str, new_role: str) -> None:
    """Change user's role (admin only)"""
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
    conn.commit()
    conn.close()


def delete_user_db(username: str) -> None:
    """Delete user permanently (admin only)"""
    conn = _conn()
    cur = conn.cursor()
    # Delete user's tickets, notifications, etc.
    cur.execute("DELETE FROM tickets WHERE owner = ?", (username,))
    cur.execute("DELETE FROM notifications WHERE user = ?", (username,))
    cur.execute("DELETE FROM ratings WHERE user = ?", (username,))
    cur.execute("DELETE FROM activity WHERE user = ?", (username,))
    cur.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def assign_ticket(ticket_id: int, assigned_to: str) -> None:
    """Assign ticket to support user"""
    conn = _conn()
    cur = conn.cursor()

    # Add column if it doesn't exist
    try:
        cur.execute("ALTER TABLE tickets ADD COLUMN assigned_to TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    cur.execute("""
        UPDATE tickets
        SET assigned_to = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (assigned_to, ticket_id))
    conn.commit()
    conn.close()


def update_ticket_priority(ticket_id: int, priority: str) -> None:
    """Update ticket priority"""
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tickets
        SET priority = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (priority, ticket_id))
    conn.commit()
    conn.close()


def delete_ticket_db(ticket_id: int) -> None:
    """Delete ticket permanently"""
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM attachments WHERE ticket_id = ?", (ticket_id,))
    cur.execute("DELETE FROM ratings WHERE ticket_id = ?", (ticket_id,))
    cur.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()