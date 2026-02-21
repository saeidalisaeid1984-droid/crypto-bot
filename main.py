import requests
import time
import os

# ================= CONFIG =================

TELEGRAM_BOT_TOKEN = "8290039493:AAHz27Otu5LvTVqKCAvFHoS55Oj2wM7quEY"
TELEGRAM_CHAT_ID = "8207227866"

SCAN_INTERVAL = 300
MIN_LIQUIDITY = 30000
MIN_VOLUME = 50000
VOLUME_SPIKE_RATIO = 2

DEX_API = "https://api.dexscreener.com/latest/dex/pairs"

sent_tokens = set()

# ================= TELEGRAM =================

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except:
        pass

# ================= ANALYSIS =================

def analyze(pair):
    try:
        price = float(pair.get("priceUsd", 0))
        volume = float(pair.get("volumeUsd24h", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        symbol = pair.get("baseToken", {}).get("symbol")
        chain = pair.get("chainId")

        if liquidity < MIN_LIQUIDITY:
            return None

        if volume < MIN_VOLUME:
            return None

        if volume < MIN_VOLUME * VOLUME_SPIKE_RATIO:
            return None

        if symbol in sent_tokens:
            return None

        entry = price
        target1 = round(price * 1.10, 8)
        target2 = round(price * 1.20, 8)
        stop = round(price * 0.92, 8)

        strength = "🔥 انفجار قوي"
        time_est = "15 - 60 دقيقة"

        message = f"""
🚀 <b>إشارة انفجار جديدة</b>

💎 العملة: {symbol}
🌐 الشبكة: {chain}

💰 السعر: {price}
💧 السيولة: {liquidity}
📊 الفوليوم: {volume}

🎯 الدخول: {entry}
🎯 الهدف 1: {target1}
🎯 الهدف 2: {target2}
🛑 الستوب: {stop}

⚡ القوة: {strength}
⏳ الزمن المتوقع: {time_est}
"""

        sent_tokens.add(symbol)

        return message

    except:
        return None

# ================= MAIN LOOP =================

def run():
    print("Bot Running 24/7...")

    while True:
        try:
            response = requests.get(DEX_API, timeout=15)
            data = response.json()

            for pair in data.get("pairs", []):
                result = analyze(pair)
                if result:
                    send_message(result)
                    print("Signal Sent")

        except:
            pass

        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    run()
