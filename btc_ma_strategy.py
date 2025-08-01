import time
import os
import math
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET, testnet=True)

symbol = "BTCUSDT"
quantity = 0.001
short_window = 7
long_window = 25
interval = Client.KLINE_INTERVAL_1MINUTE

order_history = []  # Per tenere traccia degli ultimi ordini
profit_cumulative = 0.0

def get_balance_usdt():
    balances = client.get_account()['balances']
    for b in balances:
        if b['asset'] == 'USDT':
            return float(b['free'])
    return 0.0

def get_klines():
    klines = client.get_klines(symbol=symbol, interval=interval, limit=long_window+1)
    closes = [float(k[4]) for k in klines]
    return closes

def moving_averages(prices):
    short_ma = sum(prices[-short_window:]) / short_window
    long_ma = sum(prices[-long_window:]) / long_window
    return short_ma, long_ma

def place_order(side, qty):
    global profit_cumulative
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=qty
        )
        price = float(order['fills'][0]['price'])
        order_history.append({"id": order['orderId'], "side": side, "price": price})
        if len(order_history) > 5:
            order_history.pop(0)

        print(f"✅ {side} eseguito - ID: {order['orderId']} - Prezzo: {price}")

        # Aggiorna saldo
        saldo = get_balance_usdt()
        print(f"💰 Saldo attuale: {saldo:.2f} USDT")

        # Stima PnL (solo se SELL dopo BUY)
        if side == "SELL" and len(order_history) >= 2:
            last_buy = [o for o in order_history if o['side'] == "BUY"][-1]
            pnl = (price - last_buy['price']) * (qty)
            profit_cumulative += pnl
            print(f"📈 Profitto cumulativo stimato: {profit_cumulative:.2f} USDT")

        return order

    except BinanceAPIException as e:
        print(f"❌ Errore API Binance: {e.message}")
        return None

print("🚀 Trading bot avviato su Binance Testnet (ordini REALI)...")

while True:
    try:
        prices = get_klines()
        short_ma, long_ma = moving_averages(prices)
        last_price = prices[-1]

        signal = "BUY" if short_ma > long_ma else "SELL"
        print(f"\n📊 Prezzo attuale: {last_price} | Segnale: {signal}")

        place_order(signal, quantity)

        print("📜 Ultimi ordini registrati:")
        for o in order_history:
            print(f"   • {o['side']} @ {o['price']} (ID {o['id']})")

    except Exception as e:
        print(f"⚠️ Errore nel ciclo principale: {str(e)}")

    time.sleep(60)






