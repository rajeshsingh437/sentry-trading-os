"""
SENTRY — storage.py
Phase 2: Durable persistence layer.

What this does:
The dashboard (dashboard/index.html) was built around the browser's
localStorage — journal, trade plans, checklists, capital plan, and more,
all saved as separate localStorage keys. That's convenient for the app's
own logic, but localStorage alone does not survive well across machines
and can be cleared by browser/profile resets.

This file gives every one of those keys a permanent home in a single
SQLite file (sentry.db) that sits next to main.py. Moving to a new
laptop is then just: copy the whole SENTRY folder (which includes
sentry.db) and run the app — everything comes with it.

This is a generic key -> value store (mirroring localStorage's own
shape) rather than a rigid trades table. That's a deliberate choice for
this phase: it gets every existing feature (journal, plans, checklists,
capital plan, filters, etc.) durably saved with zero risk to the
5000+ lines of dashboard logic already built. A dedicated `trades`
table matching the frozen TLE spec (for fast analytics queries, Edge
Drift Monitor, etc.) is a separate, additive step planned for Phase 3
once the Trade Journal is being wired up directly — see
PROJECT_MASTER.md Section 3.1 for the reasoning.
"""

import json
import pathlib
import sqlite3

DB_PATH = pathlib.Path(__file__).parent / "sentry.db"


def get_connection():
    """
    Opens a connection to sentry.db, creating the database file and the
    kv_store table on first run if they don't exist yet.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kv_store (
            key        TEXT PRIMARY KEY,
            value      TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    return conn


def get_item(key: str):
    """Returns the stored string value for a key, or None if not set."""
    conn = get_connection()
    row = conn.execute(
        "SELECT value FROM kv_store WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return row[0] if row else None


def set_item(key: str, value: str):
    """Saves (or updates) a key's value. Value is stored as-is (a string,
    the same JSON-stringified format the dashboard already uses)."""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO kv_store (key, value, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
        """,
        (key, value),
    )
    conn.commit()
    conn.close()


def remove_item(key: str):
    conn = get_connection()
    conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))
    conn.commit()
    conn.close()


def get_all_items() -> dict:
    """Returns every saved key/value pair as a plain dict — used once at
    app startup to hydrate the dashboard's localStorage."""
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM kv_store").fetchall()
    conn.close()
    return {key: value for key, value in rows}


if __name__ == "__main__":
    # Running this file directly (`python storage.py`) creates sentry.db
    # and confirms it's working, without needing the desktop app open.
    get_connection()
    existing = get_all_items()
    print(f"sentry.db ready at: {DB_PATH}")
    print(f"Currently stores {len(existing)} key(s): {list(existing.keys())}")
