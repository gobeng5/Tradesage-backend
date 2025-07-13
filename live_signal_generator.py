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

# === API Fetch ===
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
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        return data.get("Time Series FX (15min)", {})
    except Exception as e:
        print(f"❌ Request failed for {from_symbol}/{to_symbol}: {e}")
        return {}

def parse_candle_data(candles):
    timestamps = sorted(candles.keys(), reverse=True)
    opens = [float(candles[t]["1. open"]) for t in timestamps]
    highs = [float(candles[t]["2. high"]) for t in timestamps]
    lows = [float(candles[t]["3. low"]) for t in timestamps]
    closes = [float(candles[t]["4. close"]) for t in timestamps]
    latest_time = timestamps[0] if timestamps else None
    latest_close = closes[0] if closes else None
    return opens, highs, lows, closes, latest_time, latest_close

# === Signal Analysis ===
def analyze_pair(pair):
    candles = fetch_candles(pair[0], pair[1])
    if not candles:
        return None

    opens, highs, lows, closes, timestamp, latest_price = parse_candle_data(candles)
    confirmations = []
    strategy_notes = []

    # RSI
    rsi = calculate_rsi(closes)
    if rsi and rsi < 30:
        confirmations.append("RSI oversold")
        strategy_notes.append(f"RSI: {rsi}")

    # MA crossover
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

    # Breakout detection
    if detect_breakout(closes):
        confirmations.append("Breakout Above Resistance")

    signal_type = "Buy" if confirmations else "Hold"
    strategy = "Composite Strategy"
    confidence = 0.6 + 0.1 * len(confirmations)
    confidence = round(min(confidence, 0.99), 2)

    # Trade levels (assume Buy setup logic)
    entry = latest_price
    take_profit = round(entry * (1 + 0.0025), 5)  # ~25 pips
    stop_loss = round(entry * (1 - 0.0015), 5)    # ~15 pips

    return {
        "pair": f"{pair[0]}/{pair[1]}",
        "timeframe": "15min",
        "strategy": strategy,
        "confirmations": confirmations,
        "indicators": strategy_notes,
        "signal_type": signal_type,
        "confidence": confidence,
        "entry": entry,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
        "timestamp": timestamp
    }

# === Signal Engine ===
def generate_live_signals():
    now = datetime.datetime.utcnow()
    if CACHE["timestamp"]:
        age = (now - CACHE["timestamp"]).total_seconds() / 60
        if age < CACHE_DURATION_MINUTES:
            print("📦 Using cached signals...")
            return {"signals": CACHE["signals"]}

    print("⚡ Fetching fresh signals...")
    signals = []
    for pair in PAIRS:
        signal = analyze_pair(pair)
        if signal:
            log_signal(signal)
            signals.append(signal)

            if signal["confidence"] >= 0.9:
                notify_telegram(signal)

    CACHE["signals"] = signals
    CACHE["timestamp"] = now
    return {"signals": signals}
