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

    # USERS (grunn-tabell)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            pw_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_login TEXT
        )
    """)

    # Sørg for at disse kolonnene finnes selv om DB allerede var opprettet før
    for stmt in [
        "ALTER TABLE users ADD COLUMN email TEXT",
        "ALTER TABLE users ADD COLUMN notify_email INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE users ADD COLUMN notify_inapp INTEGER NOT NULL DEFAULT 1",
    ]:
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass  # kolonnen finnes allerede

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

    # ARTICLES
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


def create_user(username: str, pw_hash: str, role: str = "user", email: Optional[str] = None) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, pw_hash, role, email) VALUES (?, ?, ?, ?)",
        (username, pw_hash, role, email),
    )
    conn.commit()
    conn.close()


def get_user(username: str) -> Optional[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT username, pw_hash, role, email, notify_email, notify_inapp, last_login FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_last_login(username: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_login = datetime('now') WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def update_preferences(username: str, notify_email: int, notify_inapp: int) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET notify_email = ?, notify_inapp = ? WHERE username = ?",
        (int(notify_email), int(notify_inapp), username),
    )
    conn.commit()
    conn.close()


def get_support_users() -> List[Dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT username, email, notify_email, notify_inapp FROM users WHERE role = 'support' ORDER BY username ASC")
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
# NOTIFICATIONS
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