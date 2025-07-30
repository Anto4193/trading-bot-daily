import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime

# ===== CONFIG =====
START_BALANCE = 1000.0
EMAIL_SENDER = "a.bianco93@icloud.com"
EMAIL_PASSWORD = "zeaw-pllb-qrxy-npol"
EMAIL_RECEIVER = "a.bianco93@icloud.com"

balance = START_BALANCE
btc_position = 0.0
last_price = 0.0

def fetch_data():
    data = yf.download("BTC-USD", period="200d", interval="1h")
    data.dropna(inplace=True)
    data["MA50"] = data["Close"].rolling(window=50).mean()
    data["MA200"] = data["Close"].rolling(window=200).mean()
    data["position"] = 0
    data.loc[data["MA50"] > data["MA200"], "position"] = 1
    return data

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP("smtp.mail.me.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        print("Email inviata.")
    except Exception as e:
        print("Errore nell'invio email:", e)

def trading_loop():
    global balance, btc_position, last_price
    data = fetch_data()
    signal = int(data["position"].iloc[-1])
    price = float(data["Close"].iloc[-1])
    last_price = price

    if signal == 1 and btc_position == 0.0:
        btc_position = balance / price
        balance = 0.0
        print(">>> ACQUISTO eseguito a", price)
    elif signal == 0 and btc_position > 0.0:
        balance = btc_position * price
        btc_position = 0.0
        print(">>> VENDITA eseguita a", price)

def daily_report():
    final_value = balance if btc_position == 0.0 else btc_position * last_price
    total_return = (final_value / START_BALANCE - 1) * 100
    body = f"""
Trading Bot Report - BTC (MA50/200)

Saldo finale stimato: ${final_value:.2f}
Rendimento: {total_return:.2f}%

Posizione BTC attuale: {btc_position:.6f} BTC
Ultimo prezzo: ${last_price:.2f}
"""
    send_email("Trading Bot - Report Giornaliero", body)

# ===== LOOP INFINITO 24/24 =====
while True:
    now = datetime.now()

    # Esegue il trading ogni 30 minuti
    if now.minute % 30 == 0:
        trading_loop()

    # Invia report alle 19:00
    if now.hour == 19 and now.minute == 0:
        daily_report()

    time.sleep(60)
