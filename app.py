import sqlite3
from datetime import datetime

import streamlit as st

from main import DB_PATH, init_db

CHAPTERS = {
    "chapter_i": {
        "volume": "巻 I: El Despertar",
        "title": "Capítulo I — El Despertar de las Sílabas",
        "narrative": (
            "Avanzas por el sendero. Las formas básicas comienzan a tener sentido en tu mente."
        ),
        "topics": ["Hiragana", "Katakana"],
        "goal_minutes": 300,
    },
    "chapter_ii": {
        "volume": "巻 II: Los Primeros Trazos",
        "title": "Capítulo II — Los Primeros Trazos",
        "narrative": (
            "Cada trazo que memorizas se convierte en un ancla dentro del pergamino de tu memoria."
        ),
        "topics": ["Kanji N5"],
        "goal_minutes": 400,
    },
    "chapter_iii": {
        "volume": "巻 III: La Estructura del Mundo",
        "title": "Capítulo III — La Estructura del Mundo",
        "narrative": (
            "Las reglas del idioma emergen como runas que conectan símbolos, sonidos y significado."
        ),
        "topics": ["Grammar"],
        "goal_minutes": 350,
    },
    "chapter_iv": {
        "volume": "巻 IV: El Código del Artífice",
        "title": "Capítulo IV — El Código del Artífice",
        "narrative": (
            "Forjas lógica y disciplina. Cada sesión refuerza el motor que impulsa tu progreso."
        ),
        "topics": ["Code"],
        "goal_minutes": 250,
    },
}

TOPIC_TO_CHAPTER = {
    topic: chapter_id
    for chapter_id, chapter in CHAPTERS.items()
    for topic in chapter["topics"]
}

PARCHMENT_COPPER_STYLE = """
<style>
    .stApp {
        background-color: #F4EBE1;
        color: #2C221B;
        font-family: 'Georgia', serif;
    }

    h1, h2, h3 {
        color: #8A5A2B;
        text-shadow: 1px 1px 0px rgba(184, 115, 51, 0.3);
        border-bottom: 2px solid #B87333;
        padding-bottom: 5px;
        font-family: 'Georgia', serif;
    }

    .narrative-text {
        color: #4A3728;
        font-style: italic;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    .flashcard-symbol {
        text-align: center;
        font-size: 80px;
        color: #2C221B;
        margin: 0.5rem 0 1rem 0;
        font-family: 'Georgia', serif;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FAF4ED;
        border: 1px solid #B87333;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
    }

    div.stButton > button:first-child,
    div.stFormSubmitButton > button:first-child {
        background: linear-gradient(135deg, #B87333 0%, #8A5A2B 100%);
        color: #F4EBE1;
        border: 2px solid #5C3A21;
        border-radius: 4px;
        box-shadow: 2px 2px 0px #5C3A21;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s ease;
    }

    div.stButton > button:first-child:hover,
    div.stFormSubmitButton > button:first-child:hover {
        background: linear-gradient(135deg, #8A5A2B 0%, #B87333 100%);
        transform: translate(1px, 1px);
        box-shadow: 1px 1px 0px #5C3A21;
    }

    div[data-testid="stMetricValue"] {
        color: #8A5A2B;
        font-family: 'Georgia', serif;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #FAF4ED;
        border-color: #B87333;
    }
</style>
"""


def insert_session(arco_narrativo: str, duration_minutes: int) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO study_sessions (session_timestamp, topic, duration_minutes)
            VALUES (?, ?, ?)
            """,
            (datetime.now().isoformat(timespec="seconds"), arco_narrativo, duration_minutes),
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


def fetch_chapter_minutes(chapter_id: str) -> int:
    topics = CHAPTERS[chapter_id]["topics"]
    placeholders = ", ".join("?" for _ in topics)
    query = f"""
        SELECT COALESCE(SUM(duration_minutes), 0)
        FROM study_sessions
        WHERE topic IN ({placeholders})
    """
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(query, topics)
        return int(cursor.fetchone()[0])


def chapter_progress(chapter_id: str) -> int:
    studied_minutes = fetch_chapter_minutes(chapter_id)
    goal_minutes = CHAPTERS[chapter_id]["goal_minutes"]
    return min(int((studied_minutes / goal_minutes) * 100), 100)


def chapter_label_for_topic(topic: str) -> str:
    chapter_id = TOPIC_TO_CHAPTER.get(topic)
    if chapter_id is None:
        return topic
    return CHAPTERS[chapter_id]["title"]


init_db()

st.set_page_config(page_title="Kioku Engine - The Journey", layout="centered")
st.markdown(PARCHMENT_COPPER_STYLE, unsafe_allow_html=True)

st.title("Kioku Engine — The Journey")
st.markdown(
    "<p class='narrative-text'>Tu progreso queda inscrito en el pergamino. "
    "Cada sesión avanza un capítulo de tu historia con el idioma.</p>",
    unsafe_allow_html=True,
)

chapter_options = list(CHAPTERS.keys())
selected_chapter = st.selectbox(
    "Arco narrativo",
    options=chapter_options,
    format_func=lambda chapter_id: CHAPTERS[chapter_id]["title"],
)

chapter = CHAPTERS[selected_chapter]
progress = chapter_progress(selected_chapter)

st.markdown(f"### {chapter['volume']}")
st.markdown(f"*{chapter['narrative']}*")
st.progress(progress, text=f"Progreso del Capítulo: {progress}%")

st.markdown("---")

with st.container(border=True):
    st.subheader("Registrar sesión de estudio")
    with st.form("study_session_form"):
        topic = st.selectbox("Enfoque del capítulo", chapter["topics"])
        duration_minutes = st.number_input(
            "Duración (minutos)",
            min_value=1,
            step=1,
            value=30,
        )
        submitted = st.form_submit_button("Inscribir en el pergamino")

    if submitted:
        insert_session(topic, int(duration_minutes))
        st.success("Sesión registrada. El pergamino ha sido actualizado.")
        st.rerun()

st.markdown("---")

with st.container(border=True):
    st.subheader("Prueba del sendero")
    st.markdown("*¿Qué significa este símbolo?*")
    st.markdown("<p class='flashcard-symbol'>水</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Fuego")
    with col2:
        st.button("Agua")
    with col3:
        st.button("Tierra")

st.markdown("---")

st.subheader("Crónicas recientes")
recent_sessions = fetch_recent_sessions()

if recent_sessions:
    st.table(
        {
            "ID": [row[0] for row in recent_sessions],
            "Registrado": [row[1] for row in recent_sessions],
            "Arco narrativo": [chapter_label_for_topic(row[2]) for row in recent_sessions],
            "Enfoque": [row[2] for row in recent_sessions],
            "Duración (min)": [row[3] for row in recent_sessions],
        }
    )
else:
    st.info("Aún no hay sesiones inscritas en el pergamino.")
