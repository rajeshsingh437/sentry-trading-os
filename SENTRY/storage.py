"""
SENTRY — storage.py
Phase 2: Durable key/value persistence layer (Layer A).
Phase 3: Structured trades table (Layer B), auto-synced from the journal.

Layer A (kv_store): mirrors every localStorage key the dashboard uses —
journal, plans, checklists, capital plan, filters, etc. This is the
source of truth; nothing about it changes in Phase 3.

Layer B (trades): added in Phase 3. Every time the dashboard's trade
journal is saved (localStorage key 'tos_journal_trades_v2'), this file
also parses that JSON array and mirrors it into a proper SQL table with
real columns. Layer A remains authoritative — this table is a fast,
queryable *copy*, rebuilt from Layer A on every journal save. Later
phases (Analytics, Edge Drift Monitor, Rule Engine) query this table
directly instead of parsing JSON at runtime.
"""

import json
import pathlib
import sqlite3

DB_PATH = pathlib.Path(__file__).parent / "sentry.db"

# Must match the JOURNAL_KEY constant in dashboard/index.html exactly —
# this is how we know which kv_store write is "the trade journal" and
# should trigger a Layer B resync.
JOURNAL_KEY = "tos_journal_trades_v2"


def get_connection():
    """
    Opens a connection to sentry.db, creating the database file and
    both tables on first run if they don't exist yet.
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            trade_index        INTEGER PRIMARY KEY,
            date                TEXT,
            time                TEXT,
            instrument          TEXT,
            strike              REAL,
            type                TEXT,
            strategy            TEXT,
            setup               TEXT,
            entry               REAL,
            exit_price          REAL,
            stop                REAL,
            target              REAL,
            qty                 REAL,
            risk                REAL,
            pnl                 REAL,
            mae                 REAL,
            mfe                 REAL,
            exit_time           TEXT,
            market_condition    TEXT,
            emotion             TEXT,
            confidence          REAL,
            tags                TEXT,
            mistake             TEXT,
            lesson              TEXT,
            readiness_at_entry  REAL,
            r_multiple          REAL,
            result              TEXT,
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
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
    the same JSON-stringified format the dashboard already uses).

    If this write is the trade journal, also resyncs the structured
    `trades` table (Layer B) from the new data.
    """
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

    if key == JOURNAL_KEY:
        _sync_trades_table(value)


def remove_item(key: str):
    conn = get_connection()
    conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))
    conn.commit()
    conn.close()

    if key == JOURNAL_KEY:
        _sync_trades_table("[]")


def get_all_items() -> dict:
    """Returns every saved key/value pair as a plain dict — used once at
    app startup to hydrate the dashboard's localStorage."""
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM kv_store").fetchall()
    conn.close()
    return {key: value for key, value in rows}


def _sync_trades_table(trades_json: str):
    """
    Rebuilds the structured `trades` table from the journal's JSON array.
    Called automatically by set_item/remove_item whenever the journal
    changes — never needs to be called manually.
    """
    try:
        trades = json.loads(trades_json)
        if not isinstance(trades, list):
            return
    except (json.JSONDecodeError, TypeError):
        return

    conn = get_connection()
    conn.execute("DELETE FROM trades")

    for index, t in enumerate(trades):
        if not isinstance(t, dict):
            continue

        risk = t.get("risk") or 0
        pnl = t.get("pnl") or 0
        r_multiple = round(pnl / risk, 3) if risk else None

        if pnl > 0:
            result = "WIN"
        elif pnl < 0:
            result = "LOSS"
        else:
            result = "BREAKEVEN"

        tags = t.get("tags")
        tags_str = ", ".join(tags) if isinstance(tags, list) else (tags or "")

        conn.execute(
            """
            INSERT INTO trades (
                trade_index, date, time, instrument, strike, type, strategy,
                setup, entry, exit_price, stop, target, qty, risk, pnl,
                mae, mfe, exit_time, market_condition, emotion, confidence,
                tags, mistake, lesson, readiness_at_entry, r_multiple, result,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                index,
                t.get("date"),
                t.get("time"),
                t.get("instrument"),
                t.get("strike"),
                t.get("type"),
                t.get("strategy"),
                t.get("setup"),
                t.get("entry"),
                t.get("exit"),
                t.get("stop"),
                t.get("target"),
                t.get("qty"),
                risk,
                pnl,
                t.get("mae"),
                t.get("mfe"),
                t.get("exitTime"),
                t.get("marketCondition"),
                t.get("emotion"),
                t.get("confidence"),
                tags_str,
                t.get("mistake"),
                t.get("lesson"),
                t.get("readinessAtEntry"),
                r_multiple,
                result,
            ),
        )

    conn.commit()
    conn.close()


def get_trade_stats() -> dict:
    """
    Computes headline stats directly from the structured trades table.
    Exposed to the dashboard via Api.get_trade_stats() for future phases
    (Analytics) — safe to call any time, returns zeros if there are no
    trades yet.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT pnl, r_multiple, result FROM trades WHERE pnl IS NOT NULL"
    ).fetchall()
    conn.close()

    total = len(rows)
    if total == 0:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "expectancy_r": 0,
            "profit_factor": 0,
            "avg_r": 0,
        }

    wins = [r for r in rows if r[2] == "WIN"]
    losses = [r for r in rows if r[2] == "LOSS"]

    win_rate = round((len(wins) / total) * 100, 1)

    r_values = [r[1] for r in rows if r[1] is not None]
    avg_r = round(sum(r_values) / len(r_values), 2) if r_values else 0

    gross_profit = sum(r[0] for r in wins)
    gross_loss = abs(sum(r[0] for r in losses))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss else 0

    return {
        "total_trades": total,
        "win_rate": win_rate,
        "expectancy_r": avg_r,
        "profit_factor": profit_factor,
        "avg_r": avg_r,
    }


if __name__ == "__main__":
    # Running this file directly (`python storage.py`) creates sentry.db
    # and confirms both tables exist, without needing the desktop app open.
    get_connection()
    existing = get_all_items()
    print(f"sentry.db ready at: {DB_PATH}")
    print(f"kv_store currently holds {len(existing)} key(s): {list(existing.keys())}")
    print(f"trades table stats: {get_trade_stats()}")
