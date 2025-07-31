import time
import datetime
from binance.client import Client
from binance.enums import *

# CONFIGURAZIONE
API_KEY = "WmAQiQrluxCbBjOVcSdS7oZhVUadVWOmKtEPP5FPMra1KpFMn9Wcd69qsvzoWQr0"
API_SECRET = "brF61s5EKLXTNYf9XXZ2d3WI0h0DIGSQtIVFnGGHRx6OiTAvXmgPlYP9BgDPRXNv"
SYMBOL = "BTCUSDT"
QTY = 0.001
INITIAL_CAPITAL = 10000.0

client = Client(API_KEY, API_SECRET, testnet=True)

def get_price():
    ticker = client.get_symbol_ticker(symbol=SYMBOL)
    return float(ticker["price"])

def get_balance():
    balance = client.get_asset_balance(asset='USDT')
    return float(balance['free'])

def log_trade(action, order, balance, profit_loss):
    with open("report_trading.log", "a") as f:
        f.write(f"{datetime.datetime.now()} | {action} | Ordine ID: {order['orderId']} | Qty: {order['origQty']} | Prezzo: {order['fills'][0]['price']} | Saldo: {balance:.2f} USDT | PnL Totale: {profit_loss:.2f} USDT\n")

def place_order(signal):
    try:
        order = client.create_order(
            symbol=SYMBOL,
            side=signal,
            type=ORDER_TYPE_MARKET,
            quantity=QTY
        )
        balance = get_balance()
        profit_loss = balance - INITIAL_CAPITAL
        log_trade(signal, order, balance, profit_loss)
        print(f"✅ {signal} eseguito - ID ordine: {order['orderId']}")
        print(f"💰 Saldo attuale: {balance} USDT | PnL Totale: {profit_loss} USDT")
    except Exception as e:
        print(f"❌ Errore ordine: {e}")

def get_signal():
    # Strategia molto semplice (da sostituire con la tua logica reale)
    price = get_price()
    if int(time.time()) % 2 == 0:
        return SIDE_BUY
    else:
        return SIDE_SELL

print("🚀 Trading bot avviato su Binance Testnet (ordini REALI)...")
while True:
    signal = get_signal()
    place_order(signal)
    time.sleep(30)
