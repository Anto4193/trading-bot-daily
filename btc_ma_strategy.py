import os
import time
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException

# === CONFIGURAZIONE ===
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Attiva log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# === CONNESSIONE A BINANCE TESTNET ===
client = Client(API_KEY, API_SECRET, testnet=True)
logging.info("✅ Connessione a Binance Testnet avviata...")

# Parametri di trading
symbol = "BTCUSDT"
quantity = 0.001
fast_ma_period = 5
slow_ma_period = 15
interval = "1m"

def get_klines(symbol, interval, limit):
    try:
        return client.get_klines(symbol=symbol, interval=interval, limit=limit)
    except BinanceAPIException as e:
        logging.error(f"Errore API: {e}")
        return []

def get_moving_average(data, period):
    closes = [float(x[4]) for x in data]
    return sum(closes[-period:]) / period

while True:
    try:
        klines = get_klines(symbol, interval, slow_ma_period)
        if len(klines) < slow_ma_period:
            logging.warning("Dati insufficienti per calcolare le medie mobili")
            time.sleep(10)
            continue

        fast_ma = get_moving_average(klines, fast_ma_period)
        slow_ma = get_moving_average(klines, slow_ma_period)
        current_price = float(klines[-1][4])

        logging.info(f"📊 Prezzo: {current_price} | Fast MA: {fast_ma:.2f} | Slow MA: {slow_ma:.2f}")

        # Segnale BUY
        if fast_ma > slow_ma:
            try:
                order = client.order_market_buy(symbol=symbol, quantity=quantity)
                logging.info("✅ Ordine BUY eseguito")
            except BinanceAPIException as e:
                logging.error(f"Errore ordine BUY: {e}")

        # Segnale SELL
        elif fast_ma < slow_ma:
            try:
                order = client.order_market_sell(symbol=symbol, quantity=quantity)
                logging.info("✅ Ordine SELL eseguito")
            except BinanceAPIException as e:
                logging.error(f"Errore ordine SELL: {e}")

    except Exception as e:
        logging.error(f"⚠️ Errore nel ciclo principale: {e}")

    time.sleep(10)
