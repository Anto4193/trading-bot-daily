import yfinance as yf
import pandas as pd
import ta
import time

def get_data():
    try:
        data = yf.download("BTC-USD", period="2d", interval="15m")
        if data.empty:
            print("⚠️ Nessun dato ricevuto da Yahoo Finance.")
            return pd.DataFrame()
        data["SMA_20"] = data["Close"].rolling(window=20).mean()
        data["SMA_50"] = data["Close"].rolling(window=50).mean()
        data["RSI"] = ta.momentum.RSIIndicator(data["Close"]).rsi()
        return data
    except Exception as e:
        print(f"Errore nel download dati: {e}")
        return pd.DataFrame()

def get_signal():
    df = get_data()
    if df.empty or len(df) == 0:
        print("⚠️ Dati non disponibili, nessun segnale generato.")
        return None
    
    last_row = df.iloc[-1]
    sma20 = last_row["SMA_20"]
    sma50 = last_row["SMA_50"]
    rsi = last_row["RSI"]

    if pd.isna(sma20) or pd.isna(sma50) or pd.isna(rsi):
        print("⚠️ Indicatori non calcolabili (troppi pochi dati).")
        return None

    if sma20 > sma50 and rsi < 70:
        return "BUY"
    elif sma20 < sma50 and rsi > 30:
        return "SELL"
    else:
        return "HOLD"

def trade():
    while True:
        signal = get_signal()
        if signal:
            print(f"Segnale attuale: {signal}")
        else:
            print("Nessun segnale valido.")
        time.sleep(60)

if __name__ == "__main__":
    trade()




