import sqlite3
from pathlib import Path
import importlib.util

import pytest


def _create_min_users_table(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email VARCHAR
    )
    """)
    conn.commit()


def _pragma_cols(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    return {row[1] for row in cur.fetchall()}


def _pragma_indices(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA index_list(users)")
    return {row[1] for row in cur.fetchall()}


@pytest.mark.parametrize("script_path", [
    "backend/scripts/sqlite_migrate_users_stripe.py",
    "scripts/sqlite_migrate_users_stripe.py",
])
def test_sqlite_stripe_migrator_adds_columns_and_indexes(tmp_path, monkeypatch, script_path):
    p = Path(script_path)
    if not p.exists():
        pytest.skip(f"No existe {script_path} (ruta alternativa no encontrada).")

    db_path = tmp_path / "dev_local.db"
    conn = sqlite3.connect(str(db_path))
    try:
        _create_min_users_table(conn)
    finally:
        conn.close()

    spec = importlib.util.spec_from_file_location("_sqlite_migrate_users_stripe", str(p))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)

    # soporte a DB_PATH constante y/o env var
    if hasattr(mod, "DB_PATH"):
        mod.DB_PATH = str(db_path)
    monkeypatch.setenv("DB_PATH", str(db_path))

    assert hasattr(mod, "migrate_sqlite"), "El script no expone migrate_sqlite()"
    mod.migrate_sqlite()
    mod.migrate_sqlite()  # idempotencia

    conn2 = sqlite3.connect(str(db_path))
    try:
        cols = _pragma_cols(conn2)
        expected_cols = {
            "billing_provider",
            "stripe_customer_id",
            "stripe_subscription_id",
            "stripe_price_id",
            "plan_status",
        }
        missing = expected_cols - cols
        assert not missing, f"Faltan columnas tras migración: {missing}. Cols actuales: {sorted(cols)}"

        idx = _pragma_indices(conn2)
        expected_names = {"ix_users_stripe_customer_id", "ix_users_stripe_subscription_id"}
        if expected_names.issubset(idx):
            return

        def index_columns(index_name: str):
            cur = conn2.cursor()
            cur.execute(f"PRAGMA index_info({index_name})")
            return {row[2] for row in cur.fetchall()}

        has_customer_idx = any("stripe_customer_id" in index_columns(n) for n in idx)
        has_sub_idx = any("stripe_subscription_id" in index_columns(n) for n in idx)

        assert has_customer_idx, f"No se detectó índice sobre stripe_customer_id. Indices: {sorted(idx)}"
        assert has_sub_idx, f"No se detectó índice sobre stripe_subscription_id. Indices: {sorted(idx)}"
    finally:
        conn2.close()
