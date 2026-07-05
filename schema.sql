CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_timestamp TEXT NOT NULL,
    topic TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL
);
