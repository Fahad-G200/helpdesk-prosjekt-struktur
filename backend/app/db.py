# backend/app/db.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = Path(__file__).resolve().parents[1] / "database.db"

def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ny tabellstruktur (dersom den ikke finnes)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            desc TEXT NOT NULL,
            owner TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            device TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Åpen',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Hvis du hadde gammel tabell, prøv å legge til kolonner (try/except gjør at det ikke krasjer)
    for sql in [
        "ALTER TABLE tickets ADD COLUMN category TEXT NOT NULL DEFAULT 'Annet'",
        "ALTER TABLE tickets ADD COLUMN priority TEXT NOT NULL DEFAULT 'Middels'",
        "ALTER TABLE tickets ADD COLUMN device TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE tickets ADD COLUMN created_at TEXT NOT NULL DEFAULT (datetime('now'))",
    ]:
        try:
            cur.execute(sql)
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

def add_ticket(owner: str, title: str, desc: str, category: str, priority: str, device: str) -> int:
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if owner is None:
        cur.execute("SELECT * FROM tickets ORDER BY id DESC")
    else:
        cur.execute("SELECT * FROM tickets WHERE owner = ? ORDER BY id DESC", (owner,))

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def close_ticket(ticket_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET status = 'Lukket' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()