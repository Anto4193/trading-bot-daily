import yfinance as yf
import pandas as pd
import ta
from binance.client import Client
import os
import smtplib
from email.mime.text import MIMEText

# ---- Config ----
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")
email_to = os.getenv("EMAIL_TO")

client = Client(api_key, api_secret)
ticker = "BTCUSDT"

def send_email(subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = email_user
    msg["To"] = email_to
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email_user, email_pass)
        server.sendmail(email_user, email_to, msg.as_string())

def get_signal():
    data = yf.download("BTC-USD", period="2d", interval="15m")
    data["MA7"] = data["Close"].rolling(window=7).mean()
    data["MA25"] = data["Close"].rolling(window=25).mean()
    data["RSI"] = ta.momentum.RSIIndicator(data["Close"], window=14).rsi()

    last = data.iloc[-1]
    prev = data.iloc[-2]

    signal = "HOLD"

    # Buy signal
    if prev["MA7"] < prev["MA25"] and last["MA7"] > last["MA25"] and last["RSI"] < 70:
        signal = "BUY"

    # Sell signal
    elif prev["MA7"] > prev["MA25"] and last["MA7"] < last["MA25"] and last["RSI"] > 30:
        signal = "SELL"

    return signal

def trade():
    signal = get_signal()
    print(f"Segnale attuale: {signal}")
    send_email("Segnale Bot BTC", f"Segnale attuale: {signal}")

if __name__ == "__main__":
    trade()

