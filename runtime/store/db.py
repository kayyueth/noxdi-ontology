"""SQLite substrate. Six tables + `meta`, initialised idempotently."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_VERSION = "1"
_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def open_db(path: Path | str) -> sqlite3.Connection:
    """Open a connection with FK enforcement enabled."""
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: Path | str) -> sqlite3.Connection:
    """Create the schema if not present; stamp the schema_version.

    Idempotent: running `init_db` on an existing DB is a no-op that
    still returns an open connection.
    """
    sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    conn = open_db(path)
    with conn:
        conn.executescript(sql)
        cur = conn.execute(
            "SELECT value FROM meta WHERE key = 'schema_version'"
        )
        row = cur.fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO meta(key, value) VALUES ('schema_version', ?)",
                (SCHEMA_VERSION,),
            )
        elif row["value"] != SCHEMA_VERSION:
            raise RuntimeError(
                f"schema_version mismatch: DB={row['value']!r} vs code={SCHEMA_VERSION!r}"
            )
    return conn


def table_names(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return [r["name"] for r in cur.fetchall()]
