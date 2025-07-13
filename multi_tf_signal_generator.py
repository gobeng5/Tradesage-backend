import requests
import datetime
from indicator_utils import (
    calculate_rsi, calculate_sma, calculate_ema,
    detect_bullish_engulfing, detect_pin_bar, detect_breakout
)
from signal_logger import log_signal
from notifier import notify_telegram

ALPHA_VANTAGE_API_KEY = "241RNJP4JG802QBZ"
BASE_URL = "https://www.alphavantage.co/query"
PAIR = ("EUR", "USD")  # Customize for now; scale later
THRESHOLD = 0.80  # Confidence threshold for alerts

# === Fetch Candles for a Given Timeframe ===
def fetch_candles(timeframe="15min"):
    params = {
        "function": "FX_INTRADAY",
        "from_symbol": PAIR[0],
        "to_symbol": PAIR[1],
        "interval": timeframe,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "compact"
    }
    try:
        res = requests.get(BASE_URL, params=params)
        data = res.json()
        return data.get(f"Time Series FX ({timeframe})", {})
    except Exception as e:
        print(f"❌ Fetch error [{timeframe}]: {e}")
        return {}

# === Parse Candlestick Data ===
def parse_data(candles):
    timestamps = sorted(candles.keys(), reverse=True)
    opens = [float(candles[t]["1. open"]) for t in timestamps]
    highs = [float(candles[t]["2. high"]) for t in timestamps]
    lows = [float(candles[t]["3. low"]) for t in timestamps]
    closes = [float(candles[t]["4. close"]) for t in timestamps]
    return opens, highs, lows, closes, timestamps[0]

# === Bias from Higher Timeframe ===
def detect_bias(tf):
    candles = fetch_candles(tf)
    if not candles:
        return None, None

    opens, highs, lows, closes, timestamp = parse_data(candles)
    ema = calculate_ema(closes)
    sma = calculate_sma(closes)
    rsi = calculate_rsi(closes)

    bias = None
    if ema and sma and ema > sma:
        bias = "Bullish"
    elif ema and sma and ema < sma:
        bias = "Bearish"

    if rsi and rsi < 30:
        bias = "Oversold Bullish"
    elif rsi and rsi > 70:
        bias = "Overbought Bearish"

    return bias, timestamp

# === Entry Confirmation on Lower Timeframe ===
def confirm_entry():
    candles = fetch_candles("15min")
    if not candles:
        return None

    opens, highs, lows, closes, timestamp = parse_data(candles)
    confirmations = []

    if detect_bullish_engulfing(opens, closes):
        confirmations.append("Bullish Engulfing")
    if detect_pin_bar(opens, closes, highs, lows):
        confirmations.append("Pin Bar")
    if detect_breakout(closes):
        confirmations.append("Breakout Above Resistance")

    confidence = round(min(0.6 + 0.1 * len(confirmations), 0.99), 2)
    entry = closes[0]
    take_profit = round(entry * (1 + 0.0025), 5)
    stop_loss = round(entry * (1 - 0.0015), 5)

    return {
        "confirmations": confirmations,
        "confidence": confidence,
        "entry": entry,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
        "timestamp": timestamp
    }

# === Trade Type Assignment ===
def classify_trade(h_bias, d_bias):
    if h_bias and d_bias and h_bias == d_bias:
        return "Day Trade"
    elif h_bias:
        return "Swing Trade"
    else:
        return "Intraday"

# === Main Signal Generator ===
def generate_multi_tf_signal():
    h_bias, h_time = detect_bias("60min")
    d_bias, d_time = detect_bias("240min")  # H4 bias
    macro_bias = h_bias or d_bias
    trade_type = classify_trade(h_bias, d_bias)
    lower_entry = confirm_entry()

    if not lower_entry or not macro_bias:
        print("🕒 No strong signal alignment yet.")
        return None

    signal = {
        "pair": f"{PAIR[0]}/{PAIR[1]}",
        "timeframe": "15min",
        "trade_type": trade_type,
        "macro_bias": macro_bias,
        "strategy": "Multi-TF Composite",
        "signal_type": "Buy" if macro_bias.startswith("Bullish") else "Sell",
        "confirmations": lower_entry["confirmations"],
        "confidence": lower_entry["confidence"],
        "entry": lower_entry["entry"],
        "take_profit": lower_entry["take_profit"],
        "stop_loss": lower_entry["stop_loss"],
        "timestamp": lower_entry["timestamp"]
    }

    log_signal(signal)
    if signal["confidence"] >= THRESHOLD:
        notify_telegram(signal)

    return signal
