import requests

# === Your Telegram Bot Config ===
TELEGRAM_BOT_TOKEN = "7852634025:AAGivRoIUGX8wEgXRfnkc4tu4JUZkzBKrjo"
TELEGRAM_CHAT_ID = "693362442"
BOT_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def format_signal_message(signal):
    return (
        f"🚨 *High-Confidence Trade Alert*\n"
        f"📈 *Pair:* {signal['pair']} ({signal['timeframe']})\n"
        f"🧠 *Confidence:* {signal['confidence']*100:.2f}%\n"
        f"📊 *Strategy:* {signal['strategy']}\n"
        f"📍 *Entry:* `{signal['entry']}`\n"
        f"🏁 *Take Profit:* `{signal['take_profit']}`\n"
        f"🛑 *Stop Loss:* `{signal['stop_loss']}`\n"
        f"🔄 *Outcome:* {signal.get('outcome', 'Pending')}\n"
        f"🕒 *Timestamp:* {signal['timestamp']}"
    )

def notify_telegram(signal):
    msg = format_signal_message(signal)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }

    try:
        res = requests.post(BOT_API, data=payload)
        if res.status_code == 200:
            print(f"✅ Telegram alert sent for {signal['pair']}")
        else:
            print(f"⚠️ Telegram failed: {res.text}")
    except Exception as e:
        print(f"❌ Telegram alert error: {e}")
