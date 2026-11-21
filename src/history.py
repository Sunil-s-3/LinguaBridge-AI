"""Local SQLite history. Rows never leave this computer."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "translation_history.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_text TEXT NOT NULL,
    kannada_text TEXT NOT NULL,
    hindi_text TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def _connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(_SCHEMA)
    return connection


def add_translation(
    source: str,
    kannada: str,
    hindi: str,
    db_path: Path | None = None,
) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with closing(_connect(db_path)) as connection:
        with connection:
            connection.execute(
                """
                INSERT INTO translations (source_text, kannada_text, hindi_text, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (source.strip(), kannada.strip(), hindi.strip(), timestamp),
            )


def recent_translations(
    limit: int = 20,
    db_path: Path | None = None,
) -> list[dict[str, str]]:
    with closing(_connect(db_path)) as connection:
        rows = connection.execute(
            """
            SELECT source_text, kannada_text, hindi_text, created_at
            FROM translations
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "English": row["source_text"],
            "Kannada": row["kannada_text"],
            "Hindi": row["hindi_text"],
            "Time": row["created_at"],
        }
        for row in rows
    ]


def clear_history(db_path: Path | None = None) -> None:
    with closing(_connect(db_path)) as connection:
        with connection:
            connection.execute("DELETE FROM translations")
