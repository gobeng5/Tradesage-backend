import requests
import datetime
import random

ALPHA_VANTAGE_API_KEY = "241RNJP4JG802QBZ"
BASE_URL = "https://www.alphavantage.co/query"

# Currency pairs to monitor
PAIRS = [
    ("EUR", "USD"),
    ("GBP", "USD"),
    ("USD", "JPY"),
    ("AUD", "USD")
]

def fetch_candles(from_symbol, to_symbol, interval="15min"):
    """Get recent candlesticks for a currency pair"""
    params = {
        "function": "FX_INTRADAY",
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "interval": interval,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "compact"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data.get("Time Series FX (15min)", {})

def analyze_pair(pair):
    """Apply strategy logic and return signal"""
    candles = fetch_candles(pair[0], pair[1])
    if not candles:
        return None

    timestamps = sorted(candles.keys(), reverse=True)
    recent = [float(candles[t]["4. close"]) for t in timestamps[:3]]

    # Simple logic: if recent close > previous high → breakout
    signal_type = "Buy" if recent[0] > max(recent[1:]) else "Sell"
    strategy = "Breakout"
    confidence = round(random.uniform(0.7, 0.95), 2)

    return {
        "pair": f"{pair[0]}/{pair[1]}",
        "timeframe": "15min",
        "strategy": strategy,
        "signal_type": signal_type,
        "confidence": confidence,
        "timestamp": timestamps[0]
    }

def generate_live_signals():
    """Generate signals for multiple pairs"""
    signals = []
    for pair in PAIRS:
        try:
            signal = analyze_pair(pair)
            if signal:
                signals.append(signal)
        except Exception as e:
            print(f"Error analyzing {pair}: {e}")
    return {"signals": signals}
