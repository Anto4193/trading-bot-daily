import os
import time
import pandas as pd
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException

# ==============================
# 🔹 CONFIGURAZIONE CHIAVI TESTNET
# ==============================
API_KEY = os.getenv("BINANCE_API_KEY", "Z41UsiUvJrUiSXZ2cWAXEkyzqscJq5ateXcc9nqkiIl37uIkHpDYmEOPpsjIgMS3")
API_SECRET = os.getenv("BINANCE_SECRET_KEY", "i4Yy3oAaevaZwkyD6w5EviL3zhXqo4lUZRMA0iBc1y3DImpsasAlXFoCzHqZ3G1n")

client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = 'https://testnet.binance.vision/api'  # ✅ Endpoint corretto

symbol = "BTCUSDT"
quantity = 0.001  # Quantità BTC per ordine
interval = "1m"
lookback = "60"

# ==============================
# 🔹 FUNZIONE PER OTTENERE I DATI
# ==============================
def get_historical_data():
    try:
        candles = client.get_klines(symbol=symbol, interval=interval, limit=100)
        data = pd.DataFrame(candles, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'
        ])
        data['close'] = data['close'].astype(float)
        return data
    except Exception as e:
        print(f"Errore nel recupero dati: {e}")
        return None

# ==============================
# 🔹 STRATEGIA SEMPLICE MA
# ==============================
def generate_signal(data):
    data['SMA_5'] = data['close'].rolling(window=5).mean()
    data['SMA_20'] = data['close'].rolling(window=20).mean()

    if data['SMA_5'].iloc[-1] > data['SMA_20'].iloc[-1]:
        return "BUY"
    elif data['SMA_5'].iloc[-1] < data['SMA_20'].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

# ==============================
# 🔹 FUNZIONE PER INVIARE ORDINI
# ==============================
def place_order(signal):
    try:
        if signal == "BUY":
            order = client.create_test_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
            print("✅ Ordine BUY simulato inviato.")
        elif signal == "SELL":
            order = client.create_test_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
            print("✅ Ordine SELL simulato inviato.")
        else:
            print("⚠️ Nessuna azione eseguita.")
    except BinanceAPIException as e:
        print(f"❌ Errore API Binance: {e.message}")
    except Exception as e:
        print(f"❌ Errore imprevisto: {e}")

# ==============================
# 🔹 CICLO PRINCIPALE
# ==============================
def trade():
    while True:
        data = get_historical_data()
        if data is not None:
            signal = generate_signal(data)
            price = data['close'].iloc[-1]
            print(f"📊 Prezzo attuale: {price} | Segnale: {signal}")
            place_order(signal)
        else:
            print("⚠️ Nessun dato ricevuto.")
        time.sleep(60)

if __name__ == "__main__":
    print("🚀 Trading bot avviato su Binance Testnet...")
    trade()





