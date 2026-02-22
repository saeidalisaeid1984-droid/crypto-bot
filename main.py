import requests

TOKEN = "8290039493:AAHz27Otu5LvTVqKCAvFHoS55Oj2wM7quEY"
CHAT_ID = "8207227866"

SEARCH_API = "https://api.dexscreener.com/latest/dex/search?q="

# =========================
# Telegram Sender
# =========================

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    })

# =========================
# تحليل شبه احترافي
# =========================

def analyze_crypto(query):

    try:

        data = requests.get(SEARCH_API + query, timeout=15).json()

        if "pairs" not in data:
            return "❌ لا توجد بيانات"

        pair = data["pairs"][0]

        symbol = pair.get("baseToken", {}).get("symbol")
        price = float(pair.get("priceUsd", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        volume24 = float(pair.get("volume", {}).get("h24", 0))

        # RSI تقديري بسيط (ليس حقيقي 100%)
        rsi_proxy = 50

        if volume24 > 150000:
            rsi_proxy += 10

        if liquidity > 80000:
            rsi_proxy += 5

        risk = "🟡 متوسط"

        recommendation_score = rsi_proxy / 10

        if recommendation_score > 8:
            risk = "🚀 فرصة قوية"

        elif recommendation_score < 4:
            risk = "⚠️ خطورة عالية"

        entry = price
        target1 = round(price * 1.08, 8)
        target2 = round(price * 1.15, 8)
        stop = round(price * 0.94, 8)

        return f"""
🤖 Ultra Smart Advisor

💎 العملة: {symbol}

💰 السعر: {price}

📊 السيولة: {liquidity}
📈 الفوليوم: {volume24}

⭐ نسبة التوصية: {int(recommendation_score*10)}%

⚠️ نسبة الخطورة: {risk}

🎯 الدخول: {entry}
🎯 الهدف1: {target1}
🎯 الهدف2: {target2}
🛑 وقف الخسارة: {stop}

📌 ملاحظة:
تحليل احتمالي فقط وليس ضمان ربح
"""

    except:
        return "⚠️ خطأ في التحليل"

# =========================
# قراءة أوامر Telegram
# =========================

def run_bot():

    print("🚀 Ultra AI Bot Running")

    offset = None

    while True:

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

                if text.startswith("/analyze"):

                    query = text.replace("/analyze", "").strip()

                    if query:
                        result = analyze_crypto(query)
                        send_msg(result)

        time.sleep(5)

if __name__ == "__main__":
    run_bot()
