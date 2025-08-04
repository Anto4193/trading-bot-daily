import os
import time
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException

# ==============================
# CONFIGURAZIONE LOGGING
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==============================
# CONFIGURAZIONE API BINANCE TESTNET
# ==============================
API_KEY = os.getenv("BINANCE_API_KEY", "Z41UsiUvJrUiSXZ2cWAXEkyzqscJq5ateXcc9nqkiIl37uIkHpDYmEOPpsjIgMS3")
API_SECRET = os.getenv("BINANCE_API_SECRET", "i4Yy3oAaevaZwkyD6w5EviL3zhXqo4lUZRMA0iBc1y3DImpsasAlXFoCzHqZ3G1n")

client = Client(API_KEY, API_SECRET, testnet=True)

# ==============================
# FUNZIONE DI TEST CONNESSIONE
# ==============================
def test_connection():
    try:
        account = client.get_account()
        logging.info("✅ Connessione API Testnet riuscita - Account attivo.")
        return True
    except BinanceAPIException as e:
        logging.error(f"❌ Errore connessione API: {e.message}")
        return False

# ==============================
# FUNZIONE STRATEGIA SEMPLICE (MA CROSSOVER)
# ==============================
def moving_average_strategy(symbol="BTCUSDT", qty=0.001):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=20)
        closes = [float(x[4]) for x in klines]

        fast_ma = sum(closes[-5:]) / 5
        slow_ma = sum(closes) / 20
        current_price = closes[-1]

        logging.info(f"📊 Prezzo: {current_price} | Fast MA: {fast_ma} | Slow MA: {slow_ma}")

        if fast_ma > slow_ma:
            try:
                client.order_market_buy(symbol=symbol, quantity=qty)
                logging.info("✅ Ordine BUY eseguito.")
            except BinanceAPIException as e:
                logging.error(f"Errore ordine BUY: {e.message}")
        elif fast_ma < slow_ma:
            try:
                client.order_market_sell(symbol=symbol, quantity=qty)
                logging.info("✅ Ordine SELL eseguito.")
            except BinanceAPIException as e:
                logging.error(f"Errore ordine SELL: {e.message}")
    except Exception as e:
        logging.error(f"⚠️ Errore strategia: {e}")

# ==============================
# MAIN LOOP
# ==============================
if __name__ == "__main__":
    if not test_connection():
        logging.error("🚫 Arresto script: chiave API non valida o permessi insufficienti.")
    else:
        logging.info("🚀 Trading bot avviato su Binance Testnet (ordini SIMULATI)...")
        while True:
            moving_average_strategy()
            time.sleep(10)

