import sqlite3
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "wellness_tracker.db")

def get_connection():
    """Establish connection to SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    # Enable dict factory for easier dictionary-like access
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # User Profile table (only contains a single row for settings)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        target_exam TEXT DEFAULT 'JEE',
        study_hours REAL DEFAULT 8.0,
        main_stressor TEXT DEFAULT 'Time Management',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Check if a default profile row exists, create if not
    cursor.execute("SELECT COUNT(*) FROM user_profile WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO user_profile (id, target_exam, study_hours, main_stressor)
        VALUES (1, 'JEE', 8.0, 'Time Management')
        """)
    
    # Journal Entries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        mood TEXT NOT NULL,
        journal_text TEXT NOT NULL,
        stress_level INTEGER NOT NULL,
        emotions TEXT,
        triggers TEXT,
        empathy_note TEXT,
        coping_strategy TEXT,
        mindfulness_prompt TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Chat History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def get_profile():
    """Fetch user profile details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT target_exam, study_hours, main_stressor FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "target_exam": row["target_exam"],
            "study_hours": row["study_hours"],
            "main_stressor": row["main_stressor"]
        }
    return {"target_exam": "JEE", "study_hours": 8.0, "main_stressor": "Time Management"}

def save_profile(target_exam, study_hours, main_stressor):
    """Save/update user profile details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO user_profile (id, target_exam, study_hours, main_stressor, updated_at)
    VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (target_exam, study_hours, main_stressor))
    conn.commit()
    conn.close()

def add_journal_entry(date_str, mood, journal_text, stress_level, emotions, triggers, empathy_note, coping_strategy, mindfulness_prompt):
    """Save a new journal entry and its AI analysis."""
    conn = get_connection()
    cursor = conn.cursor()
    
    emotions_str = json.dumps(emotions) if isinstance(emotions, (list, dict)) else emotions
    triggers_str = json.dumps(triggers) if isinstance(triggers, (list, dict)) else triggers
    
    cursor.execute("""
    INSERT INTO journal_entries (date, mood, journal_text, stress_level, emotions, triggers, empathy_note, coping_strategy, mindfulness_prompt)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date_str, mood, journal_text, stress_level, emotions_str, triggers_str, empathy_note, coping_strategy, mindfulness_prompt))
    conn.commit()
    conn.close()

def get_journal_entries(limit=50):
    """Retrieve journal entries sorted by date descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, date, mood, journal_text, stress_level, emotions, triggers, empathy_note, coping_strategy, mindfulness_prompt, created_at
    FROM journal_entries
    ORDER BY date DESC, id DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    entries = []
    for r in rows:
        # Load JSON fields safely
        try:
            emotions = json.loads(r["emotions"]) if r["emotions"] else []
        except:
            emotions = [e.strip() for e in r["emotions"].split(",")] if r["emotions"] else []
            
        try:
            triggers = json.loads(r["triggers"]) if r["triggers"] else []
        except:
            triggers = [t.strip() for t in r["triggers"].split(",")] if r["triggers"] else []
            
        entries.append({
            "id": r["id"],
            "date": r["date"],
            "mood": r["mood"],
            "journal_text": r["journal_text"],
            "stress_level": r["stress_level"],
            "emotions": emotions,
            "triggers": triggers,
            "empathy_note": r["empathy_note"],
            "coping_strategy": r["coping_strategy"],
            "mindfulness_prompt": r["mindfulness_prompt"],
            "created_at": r["created_at"]
        })
    return entries

def get_chat_history(limit=100):
    """Retrieve chat history sorted chronologically."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history ORDER BY id ASC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]

def add_chat_message(role, content):
    """Save a single chat message."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def clear_chat_history():
    """Clear all saved chat history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()
    
def delete_journal_entry(entry_id):
    """Delete a single journal entry by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
