import os
import time
import requests
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

# ==============================
#  CONFIGURAZIONE
# ==============================
API_KEY = "WmAQiQrluxCbBjOVcSdS7oZhVUadVWOmKtEPP5FPMra1KpFMn9Wcd69qsvzoWQr0"
API_SECRET = "brF61s5EKLXTNYf9XXZ2d3WI0h0DIGSQtIVFnGGHRx6OiTAvXmgPlYP9BgDPRXNv"

SYMBOL = "BTCUSDT"
QUANTITY = 0.001
INTERVAL = "1m"
LIMIT = 100

# ==============================
#  CLIENT BINANCE TESTNET
# ==============================
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = "https://testnet.binance.vision/api"

# ==============================
#  FUNZIONI
# ==============================
def get_klines():
    try:
        klines = client.get_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1MINUTE, limit=LIMIT)
        data = pd.DataFrame(klines, columns=['time','open','high','low','close','volume','close_time','qav','trades','tb_base_av','tb_quote_av','ignore'])
        data['close'] = data['close'].astype(float)
        return data
    except Exception as e:
        print("❌ Errore nel recupero dati:", e)
        return None

def generate_signal(df):
    df['SMA_5'] = df['close'].rolling(window=5).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()

    if df['SMA_5'].iloc[-1] > df['SMA_20'].iloc[-1]:
        return "BUY"
    elif df['SMA_5'].iloc[-1] < df['SMA_20'].iloc[-1]:
        return "SELL"
    return "HOLD"

def place_order(signal):
    try:
        if signal == "BUY":
            order = client.create_test_order(
                symbol=SYMBOL,
                side='BUY',
                type='MARKET',
                quantity=QUANTITY
            )
            print("✅ Ordine BUY inviato (TEST)")
        elif signal == "SELL":
            order = client.create_test_order(
                symbol=SYMBOL,
                side='SELL',
                type='MARKET',
                quantity=QUANTITY
            )
            print("✅ Ordine SELL inviato (TEST)")
    except BinanceAPIException as e:
        print("❌ Errore API Binance:", e.message)
    except Exception as e:
        print("⚠️ Errore generico:", e)

def trade():
    while True:
        df = get_klines()
        if df is not None:
            price = df['close'].iloc[-1]
            signal = generate_signal(df)
            print(f"\n📊 Prezzo attuale: {price:.2f} | Segnale: {signal}")
            if signal in ["BUY", "SELL"]:
                place_order(signal)
        time.sleep(10)

# ==============================
#  AVVIO BOT
# ==============================
if __name__ == "__main__":
    print("🚀 Trading bot avviato su Binance Testnet...")
    trade()






