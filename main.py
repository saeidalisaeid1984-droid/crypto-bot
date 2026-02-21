import requests
import time

# ===============================
# CONFIG
# ===============================

TOKEN = "8290039493:AAHz27Otu5LvTVqKCAvFHoS55Oj2wM7quEY"
CHAT_ID = "8207227866"

API_URL = "https://api.dexscreener.com/latest/dex/pairs"
SEARCH_URL = "https://api.dexscreener.com/latest/dex/search?q="

SCAN_TIME = 180

MAX_PRICE = 1
MIN_LIQUIDITY = 60000
MIN_VOLUME = 100000

sent_tokens = set()

# ===============================
# Telegram Sender
# ===============================

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        })
    except:
        pass

# ===============================
# Institutional Scoring Engine
# ===============================

def score_engine(pair):

    score = 5
    reasons = []

    try:

        volume24 = float(pair.get("volume", {}).get("h24", 0))
        volume5m = float(pair.get("volume", {}).get("m5", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        change5m = float(pair.get("priceChange", {}).get("m5", 0))

        if liquidity > MIN_LIQUIDITY:
            score += 2

        if volume5m > (volume24 / 288) * 3:
            score += 2
            reasons.append("سبايك فوليوم")

        if 0 < change5m < 6:
            score += 1
            reasons.append("زخم إيجابي")

        return score, reasons

    except:
        return score, reasons

# ===============================
# Analyzer Core
# ===============================

def analyze_pair(pair):

    try:

        symbol = pair.get("baseToken", {}).get("symbol")

        if not symbol:
            return None

        price = float(pair.get("priceUsd", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        volume24 = float(pair.get("volume", {}).get("h24", 0))

        if price > MAX_PRICE:
            return None

        if liquidity < MIN_LIQUIDITY:
            return None

        if volume24 < MIN_VOLUME:
            return None

        if symbol in sent_tokens:
            return None

        score, reasons = score_engine(pair)

        strength = "🟡 متوسطة"
        time_est = "1 - 3 ساعات"

        if score >= 7:
            strength = "🔥 قوية"
            time_est = "30 - 90 دقيقة"

        if score >= 9:
            strength = "🚀 انفجار وشيك"

        entry = price
        target1 = round(price * 1.1, 8)
        target2 = round(price * 1.2, 8)
        stop = round(price * 0.94, 8)

        sent_tokens.add(symbol)

        return f"""
🤖 Ultra Hunter MAX

💎 العملة: {symbol}
💰 السعر: {price}

📊 السيولة: {liquidity}
📈 حجم 24h: {volume24}

🎯 الدخول: {entry}
🎯 الهدف1: {target1}
🎯 الهدف2: {target2}
🛑 الستوب: {stop}

⚡ القوة: {strength}
⏳ الزمن المتوقع: {time_est}

📌 التحليل:
{", ".join(reasons)}
"""

    except:
        return None

# ===============================
# Manual Search Feature
# ===============================

def manual_search(query):

    try:

        data = requests.get(SEARCH_URL + query, timeout=15).json()

        if "pairs" not in data:
            return "❌ لم يتم العثور على العملة"

        return analyze_pair(data["pairs"][0]) or "❌ لا توجد فرصة قوية"

    except:
        return "⚠️ خطأ في البحث"

# ===============================
# Telegram Commands Reader
# ===============================

def run_bot():

    print("🔥 Ultra Hunter MAX Running 24/7")

    offset = None

    while True:

        try:

            updates = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={"offset": offset}
            ).json()

            if "result" in updates:

                for update in updates["result"]:

                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    text = update["message"]["text"]

                    # Manual analysis command
                    if text.startswith("/analyze"):

                        query = text.replace("/analyze", "").strip()

                        if query:
                            result = manual_search(query)
                            send_message(result)

            # Auto market scan
            market = requests.get(API_URL, timeout=15).json()

            for pair in market.get("pairs", []):
                signal = analyze_pair(pair)

                if signal:
                    send_message(signal)
                    print("Signal Sent")

        except:
            pass

        time.sleep(SCAN_TIME)

# ===============================

if __name__ == "__main__":
    run_bot()
