import time
from binance.client import Client
from binance.enums import *
import pandas as pd
import requests

# Inserisci qui le tue chiavi API Testnet
API_KEY = "WmAQiQrluxCbBjOVcSdS7oZhVUadVWOmKtEPP5FPMra1KpFMn9Wcd69qsvzoWQr0"
API_SECRET = "brF61s5EKLXTNYf9XXZ2d3WI0h0DIGSQtIVFnGGHRx6OiTAvXmgPlYP9BgDPRXNv"

BASE_URL = "https://testnet.binance.vision"

client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = BASE_URL

ticker = "BTCUSDT"
quantity = 0.001  # Quantità di BTC da comprare/vendere per ordine

position_open = False  # Per tenere traccia se abbiamo già una posizione aperta

def get_data(symbol, interval, lookback):
    url = f"{BASE_URL}/api/v3/klines?symbol={symbol}&interval={interval}&limit={lookback}"
    data = requests.get(url).json()
    frame = pd.DataFrame(data)
    frame = frame.iloc[:, 0:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame['Close'] = frame['Close'].astype(float)
    return frame

def strategy():
    df = get_data(ticker, '1m', 50)
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    if df['MA5'].iloc[-1] > df['MA20'].iloc[-1]:
        return 'BUY'
    elif df['MA5'].iloc[-1] < df['MA20'].iloc[-1]:
        return 'SELL'
    else:
        return 'HOLD'

def place_order(signal):
    global position_open
    if signal == 'BUY' and not position_open:
        order = client.create_order(
            symbol=ticker,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        print(f"✅ Ordine BUY eseguito: {order['fills'][0]['price']}")
        position_open = True

    elif signal == 'SELL' and position_open:
        order = client.create_order(
            symbol=ticker,
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        print(f"✅ Ordine SELL eseguito: {order['fills'][0]['price']}")
        position_open = False

def trade():
    while True:
        signal = strategy()
        print(f"📊 Prezzo attuale: {get_data(ticker, '1m', 1)['Close'].iloc[-1]} | Segnale: {signal}")
        place_order(signal)
        time.sleep(10)  # Controlla ogni 10 secondi

if __name__ == "__main__":
    print("🚀 Trading bot avviato su Binance Testnet...")
    trade()





