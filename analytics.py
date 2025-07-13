import sqlite3
from collections import defaultdict
from datetime import datetime

DB_NAME = "signals.db"

def get_confidence_trend(pair=None, limit=100):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
        SELECT pair, confidence, logged_at FROM signals
        ORDER BY logged_at ASC
        LIMIT ?
    """
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    conn.close()

    data = defaultdict(list)
    for row in rows:
        signal_pair = row[0]
        confidence = row[1]
        timestamp = row[2]
        if pair and signal_pair != pair:
            continue
        data[signal_pair].append({
            "x": timestamp,
            "y": round(confidence * 100, 2)
        })

    return data  # Dict of pair → confidence point list
