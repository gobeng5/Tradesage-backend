import statistics

# === RSI Calculation ===
def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, period + 1):
        delta = closes[i] - closes[i - 1]
        if delta > 0:
            gains.append(delta)
        else:
            losses.append(abs(delta))

    avg_gain = statistics.mean(gains) if gains else 0
    avg_loss = statistics.mean(losses) if losses else 0

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

# === Moving Averages ===
def calculate_sma(closes, period=14):
    if len(closes) < period:
        return None
    return round(sum(closes[-period:]) / period, 4)

def calculate_ema(closes, period=14):
    if len(closes) < period:
        return None
    k = 2 / (period + 1)
    ema = closes[0]
    for price in closes[1:]:
        ema = price * k + ema * (1 - k)
    return round(ema, 4)

# === Candlestick Pattern Detection ===
def detect_bullish_engulfing(opens, closes):
    if len(closes) < 2 or len(opens) < 2:
        return False
    return closes[-2] < opens[-2] and closes[-1] > opens[-1] and opens[-1] < closes[-2]

def detect_pin_bar(opens, closes, highs, lows):
    if len(opens) < 1:
        return False
    body = abs(closes[-1] - opens[-1])
    upper_wick = highs[-1] - max(opens[-1], closes[-1])
    lower_wick = min(opens[-1], closes[-1]) - lows[-1]
    return (body < upper_wick) or (body < lower_wick)

# === Chart Pattern Placeholder ===
def detect_breakout(closes, threshold=0.002):
    if len(closes) < 3:
        return False
    return closes[-1] > max(closes[-3:-1]) * (1 + threshold)

