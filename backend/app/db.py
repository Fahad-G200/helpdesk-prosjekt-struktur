from __future__ import annotations

import os
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional

from werkzeug.security import generate_password_hash
from .config import Config

logger = logging.getLogger(__name__)

# Bruk DB-path fra config.py
DB_PATH = Path(Config.DATABASE_PATH)


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _conn()
    cur = conn.cursor()

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

    # Opprett support/admin uten hardkodet passord
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


def user_exists(username: str) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row is not None


def create_user(username: str, pw_hash: str, role: str = "user") -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, pw_hash, role) VALUES (?, ?, ?)",
        (username, pw_hash, role),
    )
    conn.commit()
    conn.close()


def get_user(username: str) -> Optional[Dict[str, str]]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT username, pw_hash, role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_last_login(username: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET last_login = datetime('now') WHERE username = ?",
        (username,),
    )
    conn.commit()
    conn.close()


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
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id


def get_tickets(owner: Optional[str] = None) -> List[Dict[str, str]]:
    conn = _conn()
    cur = conn.cursor()
    if owner is None:
        cur.execute("SELECT * FROM tickets ORDER BY id DESC")
    else:
        cur.execute("SELECT * FROM tickets WHERE owner = ? ORDER BY id DESC", (owner,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


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