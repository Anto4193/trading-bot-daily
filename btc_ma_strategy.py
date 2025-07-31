import time
from binance.client import Client
from binance.enums import *

# === CONFIGURAZIONE ===
API_KEY = "WmAQiQrluxCbBjOVcSdS7oZhVUadVWOmKtEPP5FPMra1KpFMn9Wcd69qsvzoWQr0"
API_SECRET = "brF61s5EKLXTNYf9XXZ2d3WI0h0DIGSQtIVFnGGHRx6OiTAvXmgPlYP9BgDPRXNv"
PAIR = "BTCUSDT"
QTY = 0.001  # Quantità di test
INTERVAL = 30  # secondi tra un controllo e l'altro

client = Client(API_KEY, API_SECRET, testnet=True)

# Variabile stato posizione
position_open = False

# Funzione per ottenere le medie mobili
def get_signals():
    klines = client.get_klines(symbol=PAIR, interval=Client.KLINE_INTERVAL_1MINUTE, limit=20)
    closes = [float(x[4]) for x in klines]
    sma5 = sum(closes[-5:]) / 5
    sma20 = sum(closes) / 20
    price = closes[-1]

    if sma5 > sma20:
        return "BUY", price
    elif sma5 < sma20:
        return "SELL", price
    else:
        return "HOLD", price

# Funzione per loggare le operazioni
def log_trade(action, price):
    with open("log_trades.txt", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {action} | Prezzo: {price}\n")

# Funzione per inviare ordine di test
def place_order(side):
    try:
        order = client.create_test_order(
            symbol=PAIR,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=QTY
        )
        print(f"✅ Ordine {side} inviato (TEST)")
        log_trade(side, price)
    except Exception as e:
        print(f"❌ Errore ordine: {e}")

# LOOP principale
print("🚀 Trading bot avviato su Binance Testnet...")
while True:
    signal, price = get_signals()
    print(f"\n📊 Prezzo attuale: {price} | Segnale: {signal}")

    global position_open
    if signal == "BUY" and not position_open:
        place_order(SIDE_BUY)
        position_open = True

    elif signal == "SELL" and position_open:
        place_order(SIDE_SELL)
        position_open = False

    else:
        print("⏸ Nessuna nuova operazione.")

    time.sleep(INTERVAL)





