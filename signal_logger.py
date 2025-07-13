import sqlite3
from datetime import datetime

DB_NAME = "signals.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT,
            timeframe TEXT,
            strategy TEXT,
            signal_type TEXT,
            confidence REAL,
            confirmations TEXT,
            indicators TEXT,
            timestamp TEXT,
            logged_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_signal(signal):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO signals (
            pair, timeframe, strategy, signal_type, confidence,
            confirmations, indicators, timestamp, logged_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        signal["pair"],
        signal["timeframe"],
        signal["strategy"],
        signal["signal_type"],
        signal["confidence"],
        ", ".join(signal.get("confirmations", [])),
        ", ".join(signal.get("indicators", [])),
        signal["timestamp"],
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()
