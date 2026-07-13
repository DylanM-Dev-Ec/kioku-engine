import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timezone
from fsrs_logic import KiokuScheduler
from main import DB_PATH, init_db

# --- INITIALIZATION ---
scheduler = KiokuScheduler()
init_db()

# --- UI CONFIGURATION & STYLES ---
st.set_page_config(page_title="Kioku Engine - Research Edition", layout="wide")

PARCHMENT_STYLE = """
<style>
    .flashcard-symbol { 
        font-size: 90px; text-align: center; color: #2D1B13; 
        background-color: #F5F1E6; padding: 30px;
        border-radius: 15px; border: 2px solid #8A5A2B;
    }
    .metric-box {
        background-color: #EFEBE9; padding: 15px;
        border-radius: 10px; text-align: center; border-left: 5px solid #8A5A2B;
    }
    .narrative-text { font-style: italic; color: #5D4037; }
</style>
"""
st.markdown(PARCHMENT_STYLE, unsafe_allow_html=True)

# --- NARRATIVE DATA ---
CHAPTERS = {
    "chapter_i": {"title": "巻一：小雨の筆跡", "meaning": "Trazos de lluvia ligera", "narrative": "Las formas básicas comienzan a tener sentido."},
    "chapter_ii": {"title": "巻二：墨に宿る影", "meaning": "Siluetas en la tinta", "narrative": "Cada trazo es un ancla en tu memoria."},
    "chapter_iii": {"title": "巻三：言の葉の水脈", "meaning": "Cauce de palabras", "narrative": "Las reglas emergen como runas conectoras."},
    "chapter_iv": {"title": "巻四：記憶を導く灯台", "meaning": "El faro del recuerdo", "narrative": "La lógica impulsa tu progreso científico."}
}

# --- SIDEBAR: SCIENTIFIC METRICS (XAI SECTION) ---
with st.sidebar:
    st.header("📊 Métricas de Retención")
    stats = scheduler.get_memory_stats()
    
    st.markdown("---")
    st.metric("Estabilidad Media (S)", f"{stats['avg_stability']:.1f} días", 
              help="Tiempo estimado para que la probabilidad de recuerdo caiga al 90%.")
    
    st.metric("Dificultad Promedio (D)", f"{stats['avg_difficulty']:.1f}/10", 
              help="Complejidad intrínseca de los términos en tu base de datos.")
    
    st.write(f"**Total de conocimiento:** {stats['total_cards']} términos")
    st.progress(max(0, (stats['total_cards'] - stats['new_count']) / max(1, stats['total_cards'])), 
                text="Madurez del Pergamino")
    
    st.caption("Basado en el modelo de memoria de 3 componentes de FSRS v6.")

# --- MAIN INTERFACE ---
st.title("Kioku Engine — The Journey")
st.markdown(f"<p class='narrative-text'>Capítulo actual seleccionado: {CHAPTERS['chapter_i']['title']}</p>", unsafe_allow_html=True)

col_main, col_stats = st.columns([3, 4])

with col_main:
    # 1. CORE SECTION: REVIEW SESSION
    st.subheader("Prueba del sendero")
    due_cards = scheduler.get_due_cards()

    if not due_cards:
        st.success("¡Tu mente está al día! No hay pendientes en el pergamino. 🌸")
    else:
        current_card = due_cards
        card_id, front, back = current_card, current_card[3], current_card[4]

        with st.container(border=True):
            st.markdown(f"<div class='flashcard-symbol'>{front}</div>", unsafe_allow_html=True)
            
            if "show_answer" not in st.session_state: st.session_state.show_answer = False

            if not st.session_state.show_answer:
                if st.button("Revelar conocimiento", use_container_width=True):
                    st.session_state.show_answer = True
                    st.rerun()
            else:
                st.markdown(f"### **Significado:** {back}")
                st.write("¿Qué tan bien lo recordaste?")
                
                c1, c2, c3, c4 = st.columns(4)
                ratings = [("Otra vez", 1), ("Difícil", 2), ("Bien", 3), ("Fácil", 4)]
                for i, (label, val) in enumerate(ratings):
                    with [c1, c2, c3, c4][i]:
                        if st.button(label, key=f"btn_{val}"):
                            scheduler.update_card(card_id, val)
                            st.session_state.show_answer = False
                            st.rerun()

with col_stats:
    # 2. MINI DASHBOARD
    st.subheader("Estado de la Memoria")
    if due_cards:
        # Calculate current Retrievability (R) for the top card
        # Formula: R = (1 + elapsed_days / (9 * stability))^-1
        s = current_card[5] # stability index
        e = current_card[6] # elapsed_days index
        retrievability = (1 + e / (9 * s))**-1 if s > 0 else 1.0
        
        st.write(f"**Retentividad Actual:** {retrievability*100:.1f}%")
        st.info(f"💡 Este término tiene una dificultad de {current_card[7]:.1f}/10.")
    else:
        st.write("Sin datos de sesión activa.")

st.markdown("---")

# 3. ADD NEW KNOWLEDGE
with st.expander("Inscribir nuevo conocimiento"):
    with st.form("new_card"):
        f, b = st.text_input("Kanji"), st.text_input("Significado")
        if st.form_submit_button("Inscribir") and f and b:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT INTO cards (front, back, due) VALUES (?, ?, ?)",
                             (f, b, datetime.now(timezone.utc).isoformat()))
            st.rerun()

st.caption("Kioku Engine v2.1 | Powered by FSRS v6 | Research-ready for MEXT Scholarship")