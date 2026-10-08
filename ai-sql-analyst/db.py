"""Read-only SQLite schema and query tools used by the SQL agent."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import sqlglot
from sqlglot import exp

MAX_ROWS = 500
QUERY_TIMEOUT_SECONDS = 10


def _connect_readonly(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Database file not found: {path}")
    uri = f"file:{quote(path.as_posix(), safe='/:')}?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=QUERY_TIMEOUT_SECONDS)
    connection.set_authorizer(_read_only_authorizer)
    connection.set_progress_handler(lambda: 1, QUERY_TIMEOUT_SECONDS * 100_000)
    return connection


def _read_only_authorizer(action: int, arg1: str | None, arg2: str | None,
                          database: str | None, trigger: str | None) -> int:
    denied = {
        sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE,
        sqlite3.SQLITE_ALTER_TABLE, sqlite3.SQLITE_DROP_TABLE,
        sqlite3.SQLITE_DROP_INDEX, sqlite3.SQLITE_DROP_VIEW,
        sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_VIEW, sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH,
    }
    return sqlite3.SQLITE_DENY if action in denied else sqlite3.SQLITE_OK


def inspect_schema(db_path: str | Path) -> str:
    """Return table names, columns, and foreign keys for prompt context."""
    with _connect_readonly(db_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        if not tables:
            return "No user tables found."
        chunks: list[str] = []
        for (table,) in tables:
            # Table name came from sqlite_master and is quoted as an identifier.
            safe_name = table.replace('"', '""')
            columns = connection.execute(f'PRAGMA table_info("{safe_name}")').fetchall()
            foreign_keys = connection.execute(f'PRAGMA foreign_key_list("{safe_name}")').fetchall()
            col_text = ", ".join(f"{row[1]} ({row[2] or 'type unknown'})" for row in columns)
            chunk = f"Table {table}: {col_text}"
            if foreign_keys:
                refs = ", ".join(f"{fk[3]} -> {fk[2]}.{fk[4]}" for fk in foreign_keys)
                chunk += f"\n  Foreign keys: {refs}"
            chunks.append(chunk)
        return "\n".join(chunks)


def validate_read_query(sql: str) -> str:
    """Allow one read-only SELECT statement and cap its result size."""
    cleaned = sql.strip().removesuffix(";").strip()
    if not cleaned:
        raise ValueError("The model returned an empty SQL query.")
    try:
        statements = sqlglot.parse(cleaned, read="sqlite")
    except sqlglot.errors.ParseError as exc:
        raise ValueError(f"Could not parse the generated SQL: {exc}") from exc
    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only one SQL statement can be executed at a time.")
    tree = statements[0]
    if not isinstance(tree, exp.Query):
        raise ValueError("Only read-only SELECT queries are allowed.")
    if any(isinstance(node, (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter,
                             exp.Create, exp.Command, exp.Merge)) for node in tree.walk()):
        raise ValueError("The query contains a write or administrative operation.")
    if not tree.args.get("limit"):
        tree = tree.limit(MAX_ROWS)
    else:
        limit_value = tree.args["limit"].expression
        try:
            if int(limit_value.this) > MAX_ROWS:
                tree.set("limit", exp.Limit(expression=exp.Literal.number(MAX_ROWS)))
        except (AttributeError, TypeError, ValueError):
            tree.set("limit", exp.Limit(expression=exp.Literal.number(MAX_ROWS)))
    return tree.sql(dialect="sqlite")


def run_read_query(db_path: str | Path, sql: str) -> tuple[pd.DataFrame, str]:
    safe_sql = validate_read_query(sql)
    with _connect_readonly(db_path) as connection:
        frame = pd.read_sql_query(safe_sql, connection)
    return frame, safe_sql
