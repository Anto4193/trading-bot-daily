import time
import pandas as pd
import numpy as np
from binance.client import Client

# Configurazione API Binance (Testnet)
API_KEY = "Z41UsiUvJrUiSXZ2cWAXEkyzqscJq5ateXcc9nqkiIl37uIkHpDYmEOPpsjIgMS3"
API_SECRET = "i4Yy3oAaevaZwkyD6w5EviL3zhXqo4lUZRMA0iBc1y3DImpsasAlXFoCzHqZ3G1n"

client = Client(API_KEY, API_SECRET, testnet=True)

# Parametri strategia
SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1HOUR
LOOKBACK_SHORT = 10
LOOKBACK_LONG = 50
TRAILING_STOP_PCT = 0.10
QUANTITY = 0.001  # quantità BTC da acquistare

position_open = False
entry_price = 0.0
max_price = 0.0

def get_data(symbol, interval, limit=100):
    """Scarica i dati storici da Binance."""
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=[
        'timestamp','open','high','low','close','volume','close_time',
        'quote_asset_volume','number_of_trades','taker_buy_base','taker_buy_quote','ignore'
    ])
    data["close"] = data["close"].astype(float)
    return data

while True:
    try:
        # Scarica dati più recenti
        df = get_data(SYMBOL, INTERVAL)

        # Calcola medie mobili
        short_ma = df["close"].tail(LOOKBACK_SHORT).mean()
        long_ma = df["close"].tail(LOOKBACK_LONG).mean()
        price = df["close"].iloc[-1]

        global position_open, entry_price, max_price

        # Entrata LONG
        if not position_open and short_ma > long_ma:
            order = client.order_market_buy(
                symbol=SYMBOL,
                quantity=QUANTITY
            )
            entry_price = price
            max_price = price
            position_open = True
            print(f"💰 Entrata LONG a {price}")

        # Aggiorna trailing stop e valuta uscita
        if position_open:
            max_price = max(max_price, price)
            stop_price = max_price * (1 - TRAILING_STOP_PCT)

            if price <= stop_price or short_ma < long_ma:
                order = client.order_market_sell(
