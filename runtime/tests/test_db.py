"""SQLite substrate tests."""

from __future__ import annotations

import pytest

from runtime.store import SCHEMA_VERSION, init_db, open_db
from runtime.store.db import table_names


EXPECTED_TABLES = {
    "meta",
    "object",
    "fact",
    "provenance",
    "event_index",
    "alias",
    "validation_finding",
}


def test_init_db_creates_all_tables(tmp_path):
    db_path = tmp_path / "case.db"
    conn = init_db(db_path)
    try:
        names = set(table_names(conn))
        assert EXPECTED_TABLES.issubset(names), names
    finally:
        conn.close()


def test_init_db_stamps_schema_version(tmp_path):
    db_path = tmp_path / "case.db"
    conn = init_db(db_path)
    try:
        row = conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()
        assert row["value"] == SCHEMA_VERSION
    finally:
        conn.close()


def test_init_db_is_idempotent(tmp_path):
    db_path = tmp_path / "case.db"
    c1 = init_db(db_path)
    c1.close()
    # Second call must not raise, must not duplicate meta rows.
    c2 = init_db(db_path)
    try:
        n = c2.execute(
            "SELECT COUNT(*) AS n FROM meta WHERE key='schema_version'"
        ).fetchone()["n"]
        assert n == 1
        assert set(table_names(c2)).issuperset(EXPECTED_TABLES)
    finally:
        c2.close()


def test_foreign_keys_are_enforced(tmp_path):
    db_path = tmp_path / "case.db"
    conn = init_db(db_path)
    try:
        # Inserting a fact whose subject_id does not exist must fail
        # (FKs are ON).
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO fact(fact_id, subject_id, predicate, "
                "value_kind, status, observed_at) "
                "VALUES ('f1','no_such_obj','p','text','OBSERVED','2026-01-01T00:00:00')"
            )
            conn.commit()
    finally:
        conn.close()


def test_meta_stores_schema_version_only_once(tmp_path):
    db_path = tmp_path / "case.db"
    conn = init_db(db_path)
    conn.close()
    conn = open_db(db_path)
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM meta").fetchone()["n"]
        assert n == 1
    finally:
        conn.close()
