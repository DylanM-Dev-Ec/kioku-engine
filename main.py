import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kioku.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def init_db() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(schema)


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
