import pandas as pd
import numpy as np
import time
import requests
from binance.client import Client

# 🔑 API Keys Testnet
API_KEY = "Z41UsiUvJrUiSXZ2cWAXEkyzqscJq5ateXcc9nqkiIl37uIkHpDYmEOPpsjIgMS3"
API_SECRET = "i4Yy3oAaevaZwkyD6w5EviL3zhXqo4lUZRMA0iBc1y3DImpsasAlXFoCzHqZ3G1n"

# Connessione a Binance Testnet
client = Client(API_KEY, API_SECRET, testnet=True)

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_15MINUTE
QUANTITY = 0.001  # Quantità piccola per test

def get_binance_data():
    """Scarica dati storici da Binance Testnet."""
    candles = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=100)
    df = pd.DataFrame(candles, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'trades', 'tbbav', 'tbqav', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df[['timestamp', 'close']]

def calculate_indicators(df):
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    delta = df['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(14).mean()
    avg_loss = pd.Series(loss).rolling(14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def get_signal(df):
    last = df.iloc[-1]
    if last["SMA_20"] > last["SMA_50"] and last["RSI"] < 70:
        return "BUY"
    elif last["SMA_20"] < last["SMA_50"] and last["RSI"] > 30:
        return "SELL"
    else:
        return "HOLD"

def place_order(signal):
    if signal == "BUY":
        order = client.create_test_order(
            symbol=SYMBOL,
            side='BUY',
            type='MARKET',
            quantity=QUANTITY
        )
        print("✅ Ordine BUY simulato:", order)
    elif signal == "SELL":
        order = client.create_test_order(
            symbol=SYMBOL,
            side='SELL',
            type='MARKET',
            quantity=QUANTITY
        )
        print("✅ Ordine SELL simulato:", order)
    else:
        print("ℹ️ Nessun ordine eseguito.")

def trade():
    df = get_binance_data()
    if df.empty:
        print("⚠️ Nessun dato ricevuto da Binance Testnet.")
        return
    df = calculate_indicators(df)
    signal = get_signal(df)
    last_price = df['close'].iloc[-1]
    print(f"📊 Prezzo attuale: {last_price:.2f} | Segnale: {signal}")
    place_order(signal)

if __name__ == "__main__":
    while True:
        trade()
        time.sleep(60)  # Attesa 1 minuto tra i cicli




