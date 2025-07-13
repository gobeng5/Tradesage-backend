import sqlite3

DB_NAME = "signals.db"

def fetch_signal_history(limit=50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pair, timeframe, signal_type, confidence, confirmations,
               indicators, timestamp, logged_at
        FROM signals
        ORDER BY logged_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "pair": row[0],
            "timeframe": row[1],
            "signal_type": row[2],
            "confidence": row[3],
            "confirmations": row[4].split(", "),
            "indicators": row[5].split(", "),
            "timestamp": row[6],
            "logged_at": row[7]
        })

    return history
