# backend/app/db.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = Path(__file__).resolve().parents[1] / "database.db"

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = _conn()
    cur = conn.cursor()

    # Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            pw_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Tickets
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
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

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

def add_ticket(owner: str, title: str, desc: str, category: str, priority: str, device: str) -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tickets (title, desc, owner, category, priority, device, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Åpen')
        """,
        (title, desc, owner, category, priority, device),
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
    cur.execute("UPDATE tickets SET status = 'Lukket' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()