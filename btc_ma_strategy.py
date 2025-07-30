import os
import time
import datetime
import smtplib
import pandas as pd
import yfinance as yf
from email.mime.text import MIMEText
from binance.client import Client

# ----------------------------
# Configurazione variabili ambiente
# ----------------------------
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# ----------------------------
# Funzione per inviare email
# ----------------------------
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECEIVER

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_RECEIVER, msg.as_string())
        server.quit()
    except Exception as e:
        print("Errore invio email:", e)

# ----------------------------
# Strategia di trading
# ----------------------------
def trading_strategy():
    ticker = "BTC-USD"
    data = yf.download(ticker, period="2d", interval="15m")
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()

    latest = data.iloc[-1]
    decision = ""

    if latest['SMA_50'] > latest['SMA_200']:
        decision = "BUY"
        try:
            # Esempio ordine di test
            order = client.create_test_order(
                symbol='BTCUSDT',
                side='BUY',
                type='MARKET',
                quantity=0.001
            )
        except Exception as e:
            print("Errore ordine di test:", e)
    elif latest['SMA_50'] < latest['SMA_200']:
        decision = "SELL"
    else:
        decision = "HOLD"

    return f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} → Segnale: {decision}"

# ----------------------------
# Ciclo principale
# ----------------------------
daily_report = []

while True:
    signal = trading_strategy()
    print(signal)
    daily_report.append(signal)

    # Invio report alle 19:00
    current_time = datetime.datetime.now().strftime("%H:%M")
    if current_time == "19:00":
        send_email("Daily Trading Bot Report", "\n".join(daily_report))
        daily_report = []

    time.sleep(1800)  # 30 minuti
