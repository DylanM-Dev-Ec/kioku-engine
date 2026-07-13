-- Table for FSRS v6 memory states
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    front TEXT NOT NULL,           -- The Kanji or vocabulary
    back TEXT NOT NULL,            -- Translation/Meaning
    stability REAL DEFAULT 0,     -- S: Time for recall probability to fall to 90%
    difficulty REAL DEFAULT 0,    -- D: Intrinsic complexity of the item
    elapsed_days INTEGER DEFAULT 0,
    scheduled_days INTEGER DEFAULT 0,
    reps INTEGER DEFAULT 0,        -- Total successful reviews
    lapses INTEGER DEFAULT 0,      -- Times the card was forgotten
    state INTEGER DEFAULT 0,       -- 0: New, 1: Learning, 2: Review, 3: Relearning
    due TEXT NOT NULL              -- Next review date (ISO format UTC)
);

-- Keep your original study_sessions table for time tracking
CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_timestamp TEXT NOT NULL,
    topic TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL
);