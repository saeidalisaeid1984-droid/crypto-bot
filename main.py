import time
import requests
import pandas as pd
import pandas_ta as ta
from binance.client import Client

# ================= CONFIG (Mego Crypto Bot) =================
BOT_TOKEN = "8290039493:AAHz27Otu5LvTVqKCAvFHoS55Oj2wM7quEY"
CHAT_ID = "8207227866"
BOT_NAME = "Mego Crypto"

client = Client()

# إعدادات الاستراتيجية الاحترافية
EMA_FAST, EMA_SLOW = 50, 200
COMPRESSION_THRESHOLD = 0.018   
VOL_EXPLOSION_STRONG = 3.2
VOL_EXPLOSION_WEAK = 2.2
WHALE_PRESSURE_MIN = 2.0
WATCHLIST_CONFIRM_CANDLES = 1.5 
MAX_WATCHLIST_AGE = 3600

sent_signals = {}
watchlist = {}
# ============================================================

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def get_market_data(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=220)
        df = pd.DataFrame(klines, columns=['time','open','high','low','close','volume','ct','qv','nt','tb','tq','i'])
        df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].apply(pd.to_numeric)
        return df
    except: return None

def check_whale_pressure(symbol):
    try:
        depth = client.get_order_book(symbol=symbol, limit=20)
        bid_vol = sum(float(b[1]) for b in depth['bids'])
        ask_vol = sum(float(a[1]) for a in depth['asks'])
        return round(bid_vol / ask_vol, 2) if ask_vol > 0 else 1
    except: return 1

def analyze(symbol):
    df = get_market_data(symbol)
    if df is None or len(df) < 200: return None

    df["EMA_F"] = ta.ema(df["close"], length=EMA_FAST)
    df["EMA_S"] = ta.ema(df["close"], length=EMA_SLOW)
    df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=14)

    last = df.iloc[-1]
    recent_20 = df.tail(20)
    recent_high, recent_low = recent_20["high"].max(), recent_20["low"].min()

    if recent_low <= 0: return None
    range_pct = (recent_high - recent_low) / recent_low
    avg_vol = recent_20["volume"].mean()

    if range_pct < COMPRESSION_THRESHOLD and last["volume"] < avg_vol:
        watchlist[symbol] = {"break_price": recent_high, "added_at": time.time(), "confirmed": 0}
        return None

    if symbol in watchlist:
        if time.time() - watchlist[symbol]["added_at"] > MAX_WATCHLIST_AGE:
            del watchlist[symbol]; return None

        breakout_price = watchlist[symbol]["break_price"]
        volume_ratio = last["volume"] / avg_vol if avg_vol > 0 else 1
        whale_pressure = check_whale_pressure(symbol)

        if last["close"] > breakout_price:
            watchlist[symbol]["confirmed"] += 1 if volume_ratio > VOL_EXPLOSION_STRONG else 0.5

        if (last["EMA_F"] > last["EMA_S"] and 
            whale_pressure > WHALE_PRESSURE_MIN and 
            watchlist[symbol]["confirmed"] >= WATCHLIST_CONFIRM_CANDLES):
            
            res = {"price": last["close"], "atr": last["ATR"], "vol_ratio": round(volume_ratio, 1), "whale": whale_pressure}
            del watchlist[symbol]
            return res
    return None

def send_signal(symbol, data):
    entry = data["price"]
    sl, tp = round(entry - data["atr"] * 1.4, 6), round(entry + data["atr"] * 2.8, 6)
    
    msg = f"""
🚀 <b>{BOT_NAME} Signal</b> 🚀

💎 <b>الزوج:</b> #{symbol}
💰 <b>سعر الدخول:</b> <code>{entry}</code>

📊 <b>قوة الانفجار:</b> {data['vol_ratio']}x
🐋 <b>ضغط الحيتان:</b> {data['whale']}x

🎯 <b>الهدف (TP):</b> <code>{tp}</code>
🛑 <b>الوقف (SL):</b> <code>{sl}</code>

⚡ <i>تم الالتقاط بواسطة نظام Mego السريع</i>
"""
    send_telegram_msg(msg)

def run():
    # رسالة الترحيب والتأكد من العمل
    welcome_text = f"✅ <b>تم تشغيل بوت {BOT_NAME} بنجاح!</b>\n\n🔍 جاري فحص سوق Binance الآن لاقتناص أقوى الفرص...\n📊 استراتيجية: Speed Breakout + Whale Pressure"
    print(f"🔥 {BOT_NAME} is Online...")
    send_telegram_msg(welcome_text)

    while True:
        try:
            tickers = client.get_ticker()
            top_symbols = sorted([t for t in tickers if t["symbol"].endswith("USDT")],
                                key=lambda x: float(x["quoteVolume"]), reverse=True)[:50]

            for t in top_symbols:
                symbol = t["symbol"]
                if symbol in sent_signals and time.time() - sent_signals[symbol] < 14400: continue
                
                signal = analyze(symbol)
                if isinstance(signal, dict):
                    send_signal(symbol, signal)
                    sent_signals[symbol] = time.time()
                time.sleep(0.2)
            time.sleep(20)
        except Exception as e:
            print(f"Error: {e}"); time.sleep(10)

if __name__ == "__main__":
    run()
