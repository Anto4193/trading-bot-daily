import yfinance as yf
import pandas as pd
import ta
import time

def get_data():
    data = yf.download("BTC-USD", period="2d", interval="15m")
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["RSI"] = ta.momentum.RSIIndicator(data["Close"], window=14).rsi()
    return data

def get_signal():
    data = get_data()
    last_row = data.tail(1)
    sma20 = last_row["SMA_20"].values[0]
    sma50 = last_row["SMA_50"].values[0]
    rsi = last_row["RSI"].values[0]

    if sma20 > sma50 and rsi < 70:
        return "BUY"
    elif sma20 < sma50 and rsi > 30:
        return "SELL"
    else:
        return "HOLD"

def trade():
    signal = get_signal()
    print(f"Signal: {signal}")

if __name__ == "__main__":
    while True:
        trade()
        time.sleep(60)



