import time
from binance.client import Client
from binance.enums import *
import pandas as pd
import numpy as np
import os

# ==============================
# CONFIGURAZIONE
# ==============================
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET, testnet=True)

SYMBOL = "BTCUSDT"
QUANTITY = 0.001  # quantità BTC da acquistare
INTERVAL = Client.KLINE_INTERVAL_1HOUR
LOOKBACK = "100 hours"

SHORT_MA = 20
LONG_MA = 50
TRAILING_STOP = 0.03  # 3% di trailing stop

position_open = False
buy_price = 0
max_price = 0

# ==============================
# FUNZIONI
# ==============================
def get_data(symbol, interval, lookback):
    """Scarica i dati storici da Binance"""
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback))
    frame = frame.iloc[:, 0:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

# ==============================
# LOOP PRINCIPALE
# ==============================
while True:
    try:
        df = get_data(SYMBOL, INTERVAL, LOOKBACK)
        short_ma = df['Close'].rolling(SHORT_MA).mean().iloc[-1]
        long_ma = df['Close'].rolling(LONG_MA).mean().iloc[-1]
        price = df['Close'].iloc[-1]

        # ===== ENTRATA =====
        if not position_open and short_ma > long_ma:
            order = client.order_market_buy(
                symbol=SYMBOL,
                quantity=QUANTITY
            )
            position_open = True
            buy_price = price
            max_price = price
            print(f"✅ Acquisto a {price}")

        # ===== USCITA =====
        elif position_open:
            max_price = max(max_price, price)
            stop_price = max_price * (1 - TRAILING_STOP)

            if price <= stop_price or short_ma < long_ma:
                order = client.order_market_sell(
                    symbol=SYMBOL,
                    quantity=QUANTITY
                )
                position_open = False
                print(f"🚨 Vendita a {price} (Trailing Stop attivato)")

        time.sleep(60)  # 1 minuto tra i cicli

    except Exception as e:
        print(f"Errore: {e}")
        time.sleep(60)
