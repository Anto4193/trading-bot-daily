import os
import time
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

# DEBUG: Controllo variabili d'ambiente
print("DEBUG API_KEY:", os.getenv("API_KEY"))
print("DEBUG API_SECRET:", "PRESENT" if os.getenv("API_SECRET") else "MISSING")

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

if not API_KEY or not API_SECRET:
    print("⚠️ Errore: API Key o Secret mancanti. Controllare variabili d'ambiente.")
else:
    print("✅ API Key e Secret trovate.")

client = Client(API_KEY, API_SECRET, testnet=True)

symbol = "BTCUSDT"
quantity = 0.001

def get_price():
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])

while True:
    try:
        price = get_price()
        print(f"📊 Prezzo attuale: {price}")
        order = client.create_test_order(
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        print("✅ Ordine BUY inviato (TEST)")
    except BinanceAPIException as e:
        print("⚠️ Errore Binance:", e)
    except Exception as e:
        print("⚠️ Errore nel ciclo principale:", e)

    time.sleep(10)







