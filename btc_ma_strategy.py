import time
import csv
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Chiavi API Binance Testnet
API_KEY = "WmAQiQrluxCbBjOVcSdS7oZhVUadVWOmKtEPP5FPMra1KpFMn9Wcd69qsvzoWQr0"
API_SECRET = "brF61s5EKLXTNYf9XXZ2d3WI0h0DIGSQtIVFnGGHRx6OiTAvXmgPlYP9BgDPRXNv"

client = Client(API_KEY, API_SECRET, testnet=True)

PAIR = "BTCUSDT"
TRADE_QUANTITY = 0.001
COOLDOWN = 60  # secondi tra operazioni
last_trade_time = 0
ENTRY_PRICE = None
TAKE_PROFIT = 1.002  # +0.2%
STOP_LOSS = 0.998   # -0.2%

# File log CSV
with open("trade_log.csv", "a", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Signal", "Price", "Action"])

def get_price():
    ticker = client.get_symbol_ticker(symbol=PAIR)
    return float(ticker['price'])

def get_moving_averages():
    klines = client.get_klines(symbol=PAIR, interval=Client.KLINE_INTERVAL_1MINUTE, limit=50)
    closes = [float(x[4]) for x in klines]
    ma7 = sum(closes[-7:]) / 7
    ma25 = sum(closes[-25:]) / 25
    return ma7, ma25

def log_trade(signal, price, action):
    with open("trade_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), signal, price, action])

def place_order(signal):
    global last_trade_time, ENTRY_PRICE
    current_time = time.time()
    price = get_price()

    if signal == "BUY":
        if current_time - last_trade_time < COOLDOWN:
            return
        try:
            client.create_test_order(symbol=PAIR, side='BUY', type='MARKET', quantity=TRADE_QUANTITY)
            ENTRY_PRICE = price
            print(f"✅ Ordine BUY inviato a {price}")
            log_trade(signal, price, "BUY")
            last_trade_time = current_time
        except BinanceAPIException as e:
            print("❌ Errore API Binance:", e)

    elif signal == "SELL" and ENTRY_PRICE is not None:
        if current_time - last_trade_time < COOLDOWN:
            return
        try:
            client.create_test_order(symbol=PAIR, side='SELL', type='MARKET', quantity=TRADE_QUANTITY)
            print(f"✅ Ordine SELL inviato a {price}")
            log_trade(signal, price, "SELL")
            last_trade_time = current_time
        except BinanceAPIException as e:
            print("❌ Errore API Binance:", e)

def trade():
    global ENTRY_PRICE
    ma7, ma25 = get_moving_averages()
    price = get_price()
    signal = "HOLD"

    if ma7 > ma25:
        signal = "BUY"
    elif ma7 < ma25 and ENTRY_PRICE is not None:
        signal = "SELL"

    if ENTRY_PRICE:
        if price >= ENTRY_PRICE * TAKE_PROFIT:
            signal = "SELL"
        elif price <= ENTRY_PRICE * STOP_LOSS:
            signal = "SELL"

    print(f"\n📊 Prezzo attuale: {price} | Segnale: {signal}")
    place_order(signal)

while True:
    trade()
    time.sleep(10)





