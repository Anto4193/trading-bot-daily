import time
import pandas as pd
import requests
from binance.client import Client
from binance.enums import *

# ===== CONFIGURAZIONE =====
API_KEY = "WmAQiQrluxCbBjOVcSdS7oZhVUadVWOmKtEPP5FPMra1KpFMn9Wcd69qsvzoWQr0"
API_SECRET = "brF61s5EKLXTNYf9XXZ2d3WI0h0DIGSQtIVFnGGHRx6OiTAvXmgPlYP9BgDPRXNv"
SYMBOL = "BTCUSDT"
QUANTITY_PERCENT = 0.02  # 2% del saldo
INTERVAL = "1m"
TRADE_ACTIVE = False
ENTRY_PRICE = 0
TRAILING_STOP = 0.003  # 0.3%

client = Client(API_KEY, API_SECRET, testnet=True)

# ===== FUNZIONI =====

def get_klines():
    url = f"https://testnet.binance.vision/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','q','n','takerb','takerq','ignore'])
    df['c'] = df['c'].astype(float)
    return df

def get_rsi(data, period=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_signal():
    df = get_klines()
    df['MA5'] = df['c'].rolling(window=5).mean()
    df['MA20'] = df['c'].rolling(window=20).mean()
    df['RSI'] = get_rsi(df['c'])
    if df['MA5'].iloc[-1] > df['MA20'].iloc[-1] and df['RSI'].iloc[-1] < 70:
        return "BUY", df['c'].iloc[-1]
    elif df['MA5'].iloc[-1] < df['MA20'].iloc[-1] and df['RSI'].iloc[-1] > 30:
        return "SELL", df['c'].iloc[-1]
    else:
        return "HOLD", df['c'].iloc[-1]

def get_balance():
    try:
        balance = client.get_asset_balance(asset='USDT')
        return float(balance['free'])
    except:
        return 1000  # fallback testnet

def calculate_quantity(price):
    balance = get_balance()
    amount = (balance * QUANTITY_PERCENT) / price
    return round(amount, 5)

def place_order(signal, price):
    global TRADE_ACTIVE, ENTRY_PRICE
    qty = calculate_quantity(price)
    if signal == "BUY" and not TRADE_ACTIVE:
        print(f"✅ Ordine BUY inviato (TEST) - Prezzo: {price}")
        TRADE_ACTIVE = True
        ENTRY_PRICE = price
    elif signal == "SELL" and TRADE_ACTIVE:
        print(f"✅ Ordine SELL inviato (TEST) - Prezzo: {price}")
        TRADE_ACTIVE = False
        ENTRY_PRICE = 0

def check_trailing_stop(current_price):
    global TRADE_ACTIVE, ENTRY_PRICE
    if TRADE_ACTIVE and current_price < ENTRY_PRICE * (1 - TRAILING_STOP):
        print(f"🔴 Trailing Stop attivato - Chiusura posizione a {current_price}")
        TRADE_ACTIVE = False
        ENTRY_PRICE = 0

# ===== LOOP PRINCIPALE =====
print("🚀 Trading bot v2 avviato su Binance Testnet...")
while True:
    signal, price = get_signal()
    print(f"📊 Prezzo attuale: {price} | Segnale: {signal}")
    check_trailing_stop(price)
    place_order(signal, price)
    time.sleep(10)




