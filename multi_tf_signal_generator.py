import requests
import datetime
from indicator_utils import (
    calculate_rsi, calculate_sma, calculate_ema,
    detect_bullish_engulfing, detect_pin_bar, detect_breakout
)
from signal_logger import log_signal
from notifier import notify_telegram

# === CONFIG ===
ALPHA_VANTAGE_API_KEY = "241RNJP4JG802QBZ"
BASE_URL = "https://www.alphavantage.co/query"
PAIRS = [
    ("EUR", "USD"), ("USD", "JPY"), ("GBP", "USD"), ("AUD", "USD"),
    ("USD", "CAD"), ("USD", "CHF"), ("NZD", "USD"), ("EUR", "JPY"),
    ("GBP", "JPY"), ("EUR", "GBP")
]
CACHE = {"signals": [], "timestamp": None}
CACHE_DURATION_MINUTES = 15

# === Thresholds for Each Session or Overlap ===
SESSION_THRESHOLDS = {
    "Sydney": 0.78,
    "Tokyo": 0.80,
    "London": 0.88,
    "New York": 0.90,
    "Tokyo-London": 0.85,
    "London-New York": 0.86
}

# Optional manual override
MANUAL_OVERRIDE_THRESHOLD = 0.50  # Lowered for testing

# === Session Detection ===
def get_current_session():
    hour = datetime.datetime.utcnow().hour
    if 22 <= hour < 2:
        return "Sydney"
    elif 2 <= hour < 9:
        return "Tokyo"
    elif 9 <= hour < 14:
        return "London"
    elif 14 <= hour < 17:
        return "London-New York"
    elif 17 <= hour < 20:
        return "New York"
    elif 8 <= hour < 9:
        return "Tokyo-London"
    else:
        return "Sydney"

def get_confidence_threshold():
    if MANUAL_OVERRIDE_THRESHOLD is not None:
        return MANUAL_OVERRIDE_THRESHOLD
    session = get_current_session()
    return SESSION_THRESHOLDS.get(session, 0.80)

# === Candle Fetching ===
def fetch_candles(from_symbol, to_symbol, interval="15min"):
    params = {
        "function": "FX_INTRADAY",
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "interval": interval,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "compact"
    }
    try:
        res = requests.get(BASE_URL, params=params)
        data = res.json()
        return data.get("Time Series FX (15min)", {})
    except Exception as e:
        print(f"❌ Error fetching {from_symbol}/{to_symbol}: {e}")
        return {}

def parse_candle_data(candles):
    timestamps = sorted(candles.keys(), reverse=True)
    if not timestamps:
        return [], [], [], [], None, None
    opens = [float(candles[t]["1. open"]) for t in timestamps]
    highs = [float(candles[t]["2. high"]) for t in timestamps]
    lows = [float(candles[t]["3. low"]) for t in timestamps]
    closes = [float(candles[t]["4. close"]) for t in timestamps]
    return opens, highs, lows, closes, timestamps[0], closes[0]

# === Signal Generator Per Pair ===
def analyze_pair(pair):
    candles = fetch_candles(pair[0], pair[1])
    if not candles:
        return None

    opens, highs, lows, closes, timestamp, entry = parse_candle_data(candles)
    confirmations = []
    strategy_notes = []

    # Indicators
    rsi = calculate_rsi(closes)
    ema = calculate_ema(closes)
    sma = calculate_sma(closes)

    if rsi is not None and rsi < 30:
        confirmations.append("RSI Oversold")
        strategy_notes.append(f"RSI={rsi:.2f}")
    if ema and sma and ema > sma:
        confirmations.append("EMA > SMA")
        strategy_notes.append(f"EMA={ema:.2f} > SMA={sma:.2f}")

    # Candle patterns
    if detect_bullish_engulfing(opens, closes):
        confirmations.append("Bullish Engulfing")
    if detect_pin_bar(opens, closes, highs, lows):
        confirmations.append("Pin Bar")
    if detect_breakout(closes):
        confirmations.append("Breakout Above Resistance")

    confidence = round(min(0.4 + 0.1 * len(confirmations), 0.99), 2)
    if not confirmations:
        print(f"🚫 No signal for {pair[0]}/{pair[1]}")
        return None

    print(f"✅ {pair[0]}/{pair[1]} | Confirmations: {confirmations} | Confidence: {confidence}")

    take_profit = round(entry * (1 + 0.0025), 5)
    stop_loss = round(entry * (1 - 0.0015), 5)

    return {
        "pair": f"{pair[0]}/{pair[1]}",
        "timeframe": "15min",
        "strategy": "Composite Strategy",
        "signal_type": "Buy",
        "trade_type": "Swing Trade",
        "macro_bias": "Bullish",
        "confirmations": confirmations,
        "confidence": confidence,
        "entry": entry,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
        "timestamp": timestamp
    }

# === Main Signal Engine ===
def generate_live_signals():
    now = datetime.datetime.utcnow()
    if CACHE["timestamp"]:
        age = (now - CACHE["timestamp"]).total_seconds() / 60
        if age < CACHE_DURATION_MINUTES:
            print("📦 Using cached signals...")
            return {"signals": CACHE["signals"]}

    session = get_current_session()
    threshold = get_confidence_threshold()
    print(f"\n⚡ Current session: {session}")
    print(f"🎯 Confidence threshold: {threshold}")

    signals = []
    for pair in PAIRS:
        signal = analyze_pair(pair)
        if signal:
            log_signal(signal)
            signals.append(signal)
            if signal["confidence"] >= threshold:
                notify_telegram(signal)

    CACHE["signals"] = signals
    CACHE["timestamp"] = now
    return {"signals": signals}
