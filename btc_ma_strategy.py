import os
import time
from binance.client import Client
from binance.enums import *

# Leggi le API Key dalle variabili di ambiente
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

print(f"DEBUG API_KEY: {API_KEY}")
print(f"DEBUG API_SECRET: {'PRESENT' if API_SECRET else 'MISSING'}")

# Inizializza client Binance con endpoint Testnet
client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://testnet.binancefuture.com/fapi'

symbol = 'BTCUSDT'
quantity = 0.001  # Quantità di test
interval = '1m'
fast_ma = 7
slow_ma = 25

# Funzione per ottenere dati storici
def get_klines():
    candles = client.futures_klines(symbol=symbol, interval=interval, limit=slow_ma+1)
    closes = [float(c[4]) for c in candles]
    return closes

# Funzione per calcolare la media mobile
def moving_average(data, period):
    return sum(data[-period:]) / period

# Funzione principale del bot
def run_bot():
    print("🚀 Trading bot avviato su Binance Testnet (ordini REALI)...")
    while True:
        try:
            closes = get_klines()
            fast = moving_average(closes, fast_ma)
            slow = moving_average(closes, slow_ma)
            current_price = closes[-1]

            print(f"\n📊 Prezzo attuale: {current_price} | Fast MA: {fast:.2f} | Slow MA: {slow:.2f}")

            if fast > slow:
                order = client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity
                )
                print(f"✅ BUY eseguito - ID ordine: {order['orderId']}")
            elif fast < slow:
                order = client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity
                )
                print(f"✅ SELL eseguito - ID ordine: {order['orderId']}")

        except Exception as e:
            print(f"⚠️ Errore nel ciclo principale: {e}")

        time.sleep(10)

if __name__ == "__main__":
    run_bot()







