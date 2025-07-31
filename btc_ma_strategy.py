import time
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

# 🔑 Chiavi API Testnet Binance
API_KEY = "WmAQiQrluxCbBjOVcSdS7oZhVUadVWOmKtEPP5FPMra1KpFMn9Wcd69qsvzoWQr0"
API_SECRET = "brF61s5EKLXTNYf9XXZ2d3WI0h0DIGSQtIVFnGGHRx6OiTAvXmgPlYP9BgDPRXNv"

# ✅ Connessione a Binance Testnet
client = Client(API_KEY, API_SECRET, testnet=True)

SYMBOL = "BTCUSDT"
QUANTITY = 0.001  # quantità BTC da acquistare/vendere

def get_data():
    """Scarica dati recenti dal mercato (ultime 50 candele)."""
    klines = client.get_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1MINUTE, limit=50)
    data = pd.DataFrame(klines, columns=['time','open','high','low','close','volume','close_time','q','n','taker_base','taker_quote','ignore'])
    data['close'] = data['close'].astype(float)
    return data

def generate_signal(df):
    """Strategia basata su medie mobili semplici."""
    short_ma = df['close'].rolling(window=5).mean()
    long_ma = df['close'].rolling(window=20).mean()

    if short_ma.iloc[-1] > long_ma.iloc[-1]:
        return "BUY"
    elif short_ma.iloc[-1] < long_ma.iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

def place_order(signal):
    """Invia un ordine reale su Binance Testnet."""
    try:
        if signal == "BUY":
            order = client.create_order(
                symbol=SYMBOL,
                side="BUY",
                type="MARKET",
                quantity=QUANTITY
            )
            print(f"✅ BUY eseguito - ID ordine: {order['orderId']}")
        elif signal == "SELL":
            order = client.create_order(
                symbol=SYMBOL,
                side="SELL",
                type="MARKET",
                quantity=QUANTITY
            )
            print(f"✅ SELL eseguito - ID ordine: {order['orderId']}")
        else:
            print("⏸ Nessuna azione (HOLD)")
    except BinanceAPIException as e:
        print(f"❌ Errore Binance: {e}")

def trade():
    while True:
        df = get_data()
        signal = generate_signal(df)
        current_price = df['close'].iloc[-1]
        print(f"📊 Prezzo attuale: {current_price:.2f} | Segnale: {signal}")
        if signal in ["BUY", "SELL"]:
            place_order(signal)
        time.sleep(60)

if __name__ == "__main__":
    print("🚀 Trading bot avviato su Binance Testnet (ordini REALI)...")
    trade()





