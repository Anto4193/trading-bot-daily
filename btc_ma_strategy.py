import yfinance as yf
import pandas as pd
import ta

def get_signal():
    # Scarica i dati di Bitcoin
    data = yf.download("BTC-USD", period="2d", interval="15m")

    # Calcolo delle medie mobili
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()

    # Correzione: garantisce che i dati RSI siano 1D
    close_prices = data["Close"].squeeze()  # Trasforma in Serie 1D
    data["RSI"] = ta.momentum.RSIIndicator(close_prices, window=14).rsi()

    # Ultima riga per segnali
    last_row = data.iloc[-1]

    # Logica base di trading
    if last_row["SMA_20"] > last_row["SMA_50"] and last_row["RSI"] < 70:
        return "BUY"
    elif last_row["SMA_20"] < last_row["SMA_50"] and last_row["RSI"] > 30:
        return "SELL"
    else:
        return "HOLD"

def trade():
    signal = get_signal()
    print(f"Segnale di trading attuale: {signal}")
    # Qui in futuro si può collegare l'ordine reale su Binance Testnet

if __name__ == "__main__":
    trade()


