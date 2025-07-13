import sqlite3
import requests
from datetime import datetime, timedelta

DB_NAME = "signals.db"
API_KEY = "YOUR_ALPHA_VANTAGE_KEY"
BASE_URL = "https://www.alphavantage.co/query"

def get_price_at(pair, timestamp):
    symbol = pair.replace("/", "")
    time_str = timestamp.split("T")[0]  # format: YYYY-MM-DD

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "apikey": API_KEY,
        "outputsize": "compact"
    }

    res = requests.get(BASE_URL, params=params)
    data = res.json()
    series = data.get("Time Series (5min)", {})

    start = datetime.fromisoformat(timestamp)
    trail = [start + timedelta(minutes=5 * i) for i in range(1, 6)]

    prices = []
    for t in trail:
        t_key = t.strftime("%Y-%m-%d %H:%M:%S")
        candle = series.get(t_key)
        if candle:
            prices.append(float(candle["4. close"]))

    return prices  # List of trail close prices

def evaluate_signal_outcome(signal):
    try:
        prices = get_price_at(signal["pair"], signal["timestamp"])
        if not prices or len(prices) < 3:
            return "Insufficient Data"

        start_price = prices[0]
        peak = max(prices)
        drop = min(prices)
        move = peak - start_price

        if move > 0.0025:
            return "🎯 Hit Target"
        elif drop < -0.0025:
            return "⚠️ Reversed"
        else:
            return "🕓 Stalled"
    except Exception as e:
        return "Error"

def tag_all_signals():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, pair, timestamp FROM signals")
    rows = cursor.fetchall()

    for row in rows:
        signal = {
            "id": row[0],
            "pair": row[1],
            "timestamp": row[2]
        }
        outcome = evaluate_signal_outcome(signal)
        cursor.execute("UPDATE signals SET outcome = ? WHERE id = ?", (outcome, signal["id"]))

    conn.commit()
    conn.close()
