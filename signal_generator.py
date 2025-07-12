import random

def generate_signals():
    # Sample currency pairs
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]
    timeframes = ["H1", "H4", "D1"]
    strategies = ["RSI", "MACD", "Price Action"]

    signals = []

    for pair in pairs:
        signal = {
            "pair": pair,
            "timeframe": random.choice(timeframes),
            "strategy": random.choice(strategies),
            "signal_type": random.choice(["buy", "sell"]),
            "confidence": round(random.uniform(0.7, 0.95), 2)
        }
        signals.append(signal)

    return {"signals": signals}
