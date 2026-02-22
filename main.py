import requests
import time

# =============================
# CONFIG
# =============================

TOKEN = "8290039493:AAHz27Otu5LvTVqKCAvFHoS55Oj2wM7quEY"
CHAT_ID = "8207227866"

SEARCH_API = "https://api.dexscreener.com/latest/dex/search?q="

# =============================
# Telegram Sender
# =============================

def send_msg(text):

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        })

    except Exception as e:
        print("Send Error:", e)

# =============================
# تحليل العملة
# =============================

def analyze_crypto(query):

    try:

        data = requests.get(SEARCH_API + query, timeout=15).json()

        if "pairs" not in data or len(data["pairs"]) == 0:
            return "❌ لم يتم العثور على العملة"

        pair = data["pairs"][0]

        symbol = pair.get("baseToken", {}).get("symbol")
        price = float(pair.get("priceUsd", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        volume24 = float(pair.get("volume", {}).get("h24", 0))

        score = 5

        if liquidity > 60000:
            score += 2

        if volume24 > 100000:
            score += 2

        recommendation = "⚠️ لا ينصح بالدخول"

        if score >= 7:
            recommendation = "🟡 فرصة جيدة"

        if score >= 9:
            recommendation = "🚀 فرصة قوية"

        entry = price
        target1 = round(price * 1.1, 8)
        target2 = round(price * 1.2, 8)
        stop = round(price * 0.94, 8)

        return f"""
🤖 Smart Crypto Advisor

💎 العملة: {symbol}
💰 السعر: {price}

📊 السيولة: {liquidity}
📈 الحجم 24h: {volume24}

⭐ التقييم: {recommendation}

🎯 الدخول: {entry}
🎯 الهدف1: {target1}
🎯 الهدف2: {target2}
🛑 الستوب: {stop}

⚠️ التحليل احتمالي فقط
"""

    except Exception as e:
        return f"⚠️ خطأ في التحليل: {e}"

# =============================
# Bot Runner (الحل الجذري الثالث)
# =============================

def run_bot():

    print("BOT STARTED")

    offset = 0

    while True:

        try:

            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}"
            response = requests.get(url, timeout=10).json()

            if "result" in response:

                for update in response["result"]:

                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    text = update["message"]["text"]

                    if text.startswith("/analyze"):

                        query = text.replace("/analyze", "").strip()

                        result = analyze_crypto(query)

                        send_msg(result)

        except Exception as e:
            print("Error:", e)

        time.sleep(5)

# =============================
# التشغيل
# =============================

if __name__ == "__main__":
    run_bot()
