import sqlite3
from datetime import datetime, timezone
from fsrs import FSRS, Card, Rating
from main import DB_PATH

class KiokuScheduler:
    def __init__(self):
        # Initialize FSRS v6 with default weights
        self.fsrs = FSRS()

    def get_due_cards(self):
        """Fetch cards that are due for review today in UTC."""
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            # Seleccionamos id, front, back para la interfaz
            cursor = conn.execute(
                "SELECT id, front, back FROM cards WHERE due <= ? ORDER BY due ASC", (now,)
            )
            return cursor.fetchall()

    def update_card(self, card_id, rating_value):
        """Apply FSRS math to a card based on user rating."""
        with sqlite3.connect(DB_PATH) as conn:
            # 1. Load current state (aseguramos el orden de las columnas)
            row = conn.execute("""
                SELECT stability, difficulty, elapsed_days, scheduled_days, 
                       reps, lapses, state, due 
                FROM cards WHERE id = ?""", (card_id,)).fetchone()
            
            if not row:
                return

            # 2. Map DB row to FSRS Card object
            card = Card()
            card.stability = row
            card.difficulty = row[2]
            card.elapsed_days = row[3]
            card.scheduled_days = row[4]
            card.reps = row[5]
            card.lapses = row[6]
            card.state = row[7]
            card.due = datetime.fromisoformat(row[8])

            # 3. Calculate next state
            now = datetime.now(timezone.utc)
            scheduling_cards = self.fsrs.repeat(card, now)
            updated_card = scheduling_cards[Rating(rating_value)].card

            # 4. Persist updated values
            conn.execute("""
                UPDATE cards SET 
                stability = ?, difficulty = ?, elapsed_days = ?, 
                scheduled_days = ?, reps = ?, lapses = ?, 
                state = ?, due = ?
                WHERE id = ?
            """, (
                updated_card.stability, updated_card.difficulty, 
                updated_card.elapsed_days, updated_card.scheduled_days, 
                updated_card.reps, updated_card.lapses, 
                updated_card.state, updated_card.due.isoformat(), 
                card_id
            ))

    def get_memory_stats(self):
        """Calculate aggregate memory metrics from the FSRS data."""
        with sqlite3.connect(DB_PATH) as conn:
            stats = conn.execute("""
                SELECT 
                    AVG(stability), 
                    AVG(difficulty), 
                    COUNT(*),
                    SUM(CASE WHEN state = 0 THEN 1 ELSE 0 END)
                FROM cards
            """).fetchone()
            
            # Manejo de casos donde la base de datos está vacía
            return {
                "avg_stability": stats if stats else 0,
                "avg_difficulty": stats[2] if stats[2] else 0,
                "total_cards": stats[3] if stats[3] else 0,
                "new_count": stats[4] if stats[4] else 0
            }