import time
import datetime
from binance.client import Client
from binance.enums import *
import pandas as pd
import numpy as np

API_KEY = "WmAQiQrluxCbBjOVcSdS7oZhVUadVWOmKtEPP5FPMra1KpFMn9Wcd69qsvzoWQr0"
API_SECRET = "brF61s5EKLXTNYf9XXZ2d3WI0h0DIGSQtIVFnGGHRx6OiTAvXmgPlYP9BgDPRXNv"

client = Client(API_KEY, API_SECRET, testnet=True)
SYMBOL = "BTCUSDT"
QUANTITY = 0.001  # quantità di test

last_signal = None
position = None
entry_price = None
stop_loss = None

# Funzione per ottenere dati storici
def get_klines():
    klines = client.get_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1MINUTE, limit=100)
    df = pd.DataFrame(klines, columns=['time', 'o', 'h', 'l', 'c', 'v', 'ct', 'qav', 'nt', 'tbbav', 'tbqav', 'ignore'])
    df['c'] = df['c'].astype(float)
    return df

def strategy(df):
    df['ma_fast'] = df['c'].rolling(window=7).mean()
    df['ma_slow'] = df['c'].rolling(window=25).mean()
    if df['ma_fast'].iloc[-1] > df['ma_slow'].iloc[-1]:
        return "BUY"
    elif df['ma_fast'].iloc[-1] < df['ma_slow'].iloc[-1]:
        return "SELL"
    return "HOLD"

def place_order(signal, price):
    global position, entry_price, stop_loss
    if signal == "BUY" and position != "LONG":
        print(f"✅ Entrata LONG a {price}")
        position = "LONG"
        entry_price = price
        stop_loss = price * 0.995
    elif signal == "SELL" and position != "SHORT":
        print(f"✅ Entrata SHORT a {price}")
        position = "SHORT"
        entry_price = price
        stop_loss = price * 1.005

def risk_management(price):
    global position, entry_price, stop_loss
    if position == "LONG":
        if price <= stop_loss:
            print("🛑 Stop Loss raggiunto. Chiusura LONG.")
            position = None
        elif price >= entry_price * 1.002:
            stop_loss = entry_price  # sposta SL a breakeven
        elif price >= entry_price * 1.005:
            print("📈 Aggiungo posizione piramidale LONG")
    elif position == "SHORT":
        if price >= stop_loss:
            print("🛑 Stop Loss raggiunto. Chiusura SHORT.")
            position = None
        elif price <= entry_price * 0.998:
            stop_loss = entry_price
        elif price <= entry_price * 0.995:
            print("📉 Aggiungo posizione piramidale SHORT")

def trade():
    global last_signal
    while True:
        df = get_klines()
        signal = strategy(df)
        price = df['c'].iloc[-1]
        print(f"\n📊 Prezzo attuale: {price} | Segnale: {signal}")

        if signal != last_signal:
            place_order(signal, price)
            last_signal = signal

        if position is not None:
            risk_management(price)

        time.sleep(5)

if __name__ == "__main__":
    print("🚀 Trading bot V4.0 avviato su Binance Testnet...")
    trade()




