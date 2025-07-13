import requests
import datetime
from indicator_utils import (
    calculate_rsi, calculate_sma, calculate_ema,
    detect_bullish_engulfing, detect_pin_bar, detect_breakout
)

ALPHA_VANTAGE_API_KEY = "241RNJP4JG802QBZ"
BASE_URL = "https://www.alphavantage.co/query"
PAIRS = [("EUR", "USD"), ("GBP", "USD"), ("USD", "JPY"), ("AUD", "USD")]

def fetch_candles(from_symbol, to_symbol, interval="15min"):
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
    candles = data.get("Time Series FX (15min)", {})
    return candles

def parse_candle_data(candles):
    timestamps = sorted(candles.keys(), reverse=True)
    opens = [float(candles[t]["1. open"]) for t in timestamps]
    highs = [float(candles[t]["2. high"]) for t in timestamps]
    lows = [float(candles[t]["3. low"]) for t in timestamps]
    closes = [float(candles[t]["4. close"]) for t in timestamps]
    latest_time = timestamps[0] if timestamps else None
    return opens, highs, lows, closes, latest_time

def analyze_pair(pair):
    try:
        candles = fetch_candles(pair[0], pair[1])
        if not candles:
            return None

        opens, highs, lows, closes, timestamp = parse_candle_data(candles)

        confirmations = []
        strategy_notes = []

        # RSI check
        rsi = calculate_rsi(closes)
        if rsi and rsi < 30:
            confirmations.append("RSI oversold")
            strategy_notes.append(f"RSI: {rsi}")

        # Moving Average crossover
        ema = calculate_ema(closes)
        sma = calculate_sma(closes)
        if ema and sma and ema > sma:
            confirmations.append("EMA crossover")
            strategy_notes.append(f"EMA: {ema} > SMA: {sma}")

        # Candlestick patterns
        if detect_bullish_engulfing(opens, closes):
            confirmations.append("Bullish Engulfing")
        if detect_pin_bar(opens, closes, highs, lows):
            confirmations.append("Pin Bar")

        # Breakout pattern
        if detect_breakout(closes):
            confirmations.append("Breakout Above Resistance")

        # Signal scoring
        signal_type = "Buy" if confirmations else "Hold"
        strategy = "Composite Strategy"
        confidence = 0.6 + 0.1 * len(confirmations)  # 60% base + 10% per confirmation
        confidence = round(min(confidence, 0.99), 2)

        return {
            "pair": f"{pair[0]}/{pair[1]}",
            "timeframe": "15min",
            "strategy": strategy,
            "confirmations": confirmations,
            "indicators": strategy_notes,
            "signal_type": signal_type,
            "confidence": confidence,
            "timestamp": timestamp
        }

    except Exception as e:
        print(f"Error analyzing {pair}: {e}")
        return None

def generate_live_signals():
    signals = []
    for pair in PAIRS:
        signal = analyze_pair(pair)
        if signal:
            signals.append(signal)
    return {"signals": signals}
