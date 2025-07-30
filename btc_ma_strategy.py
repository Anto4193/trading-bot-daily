import yfinance as yf
import pandas as pd
import time
from binance.client import Client
import os

# --- CONFIGURAZIONE API BINANCE ---
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

# --- FUNZIONE STRATEGIA DI TRADING ---
def trading_strategy():
    ticker = "BTC-USD"
    data = yf.download(ticker, period="2d", interval="15m")

    # Calcolo medie mobili
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["SMA_200"] = data["Close"].rolling(window=200).mean()

    # Prendo solo l'ultima candela
    latest = data.tail(1)

    # Estraggo valori scalari per il confronto
    sma_50 = latest["SMA_50"].iloc[0]
    sma_200 = latest["SMA_200"].iloc[0]

    if pd.isna(sma_50) or pd.isna(sma_200):
        return "HOLD"

    if sma_50 > sma_200:
        return "BUY"
    elif sma_50 < sma_200:
        return "SELL"
    else:
        return "HOLD"

# --- ESECUZIONE LOOP CONTINUO ---
while True:
    signal = trading_strategy()
    print(f"Segnale attuale: {signal}")

    # Esempio di integrazione ordine Binance (commentato per sicurezza demo)
    """
    if signal == "BUY":
        client.order_market_buy(symbol='BTCUSDT', quantity=0.001)
    elif signal == "SELL":
        client.order_market_sell(symbol='BTCUSDT', quantity=0.001)
    """

    time.sleep(900)  # 15 minuti
