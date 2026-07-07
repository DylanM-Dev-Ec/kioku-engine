import sqlite3
from datetime import datetime

import streamlit as st

from main import DB_PATH, init_db

TOPICS = ["Hiragana", "Katakana", "Kanji N5", "Grammar", "Code"]


def insert_session(topic: str, duration_minutes: int) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO study_sessions (session_timestamp, topic, duration_minutes)
            VALUES (?, ?, ?)
            """,
            (datetime.now().isoformat(timespec="seconds"), topic, duration_minutes),
        )


def fetch_recent_sessions(limit: int = 5) -> list[tuple]:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """
            SELECT id, session_timestamp, topic, duration_minutes
            FROM study_sessions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()


init_db()

st.title("Kioku Engine - Study Tracker")

with st.form("study_session_form"):
    topic = st.selectbox("Topic", TOPICS)
    duration_minutes = st.number_input("Duration (minutes)", min_value=1, step=1, value=30)
    submitted = st.form_submit_button("Submit")

if submitted:
    insert_session(topic, int(duration_minutes))
    st.success("Study session recorded successfully.")

st.subheader("Recent Sessions")
recent_sessions = fetch_recent_sessions()

if recent_sessions:
    st.table(
        {
            "ID": [row[0] for row in recent_sessions],
            "Timestamp": [row[1] for row in recent_sessions],
            "Topic": [row[2] for row in recent_sessions],
            "Duration (min)": [row[3] for row in recent_sessions],
        }
    )
else:
    st.info("No study sessions recorded yet.")
