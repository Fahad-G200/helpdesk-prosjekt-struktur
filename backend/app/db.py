# backend/app/db.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

# Plasser databasen utenfor pakken slik at den ikke slettes ved re‑deploy
DB_PATH = Path(__file__).resolve().parents[1] / "database.db"

def init_db() -> None:
    """Opprett tabellen tickets hvis den ikke eksisterer."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            desc TEXT NOT NULL,
            owner TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Åpen'
        )
    """)
    conn.commit()
    conn.close()

def add_ticket(owner: str, title: str, desc: str) -> int:
    """Sett inn en ny sak i databasen og returner id‑en."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tickets (title, desc, owner, status) VALUES (?, ?, ?, 'Åpen')",
        (title, desc, owner),
    )
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id

def get_tickets(owner: Optional[str] = None) -> List[Dict[str, str]]:
    """Hent saker. Support ser alle, vanlige brukere ser kun sine egne."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if owner is None:
        cur.execute("SELECT * FROM tickets ORDER BY id DESC")
    else:
        cur.execute(
            "SELECT * FROM tickets WHERE owner = ? ORDER BY id DESC", (owner,)
        )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def close_ticket(ticket_id: int) -> None:
    """Marker en sak som lukket."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET status = 'Lukket' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
