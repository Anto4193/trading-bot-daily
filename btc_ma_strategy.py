import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === STRATEGIA TRADING MA50/MA200 ===

data = yf.download("BTC-USD", start="2020-01-01", end="2024-12-31", interval="1d")
data.dropna(inplace=True)
data["MA50"] = data["Close"].rolling(window=50).mean()
data["MA200"] = data["Close"].rolling(window=200).mean()
data["position"] = 0
data.loc[data["MA50"] > data["MA200"], "position"] = 1

balance = 1000.0
btc_position = 0.0

for i in range(len(data)):
    price = float(data["Close"].iloc[i])
    signal = int(data["position"].iloc[i])

    if signal == 1 and btc_position == 0.0:
        btc_position = balance / price
        balance = 0.0
    elif signal == 0 and btc_position > 0.0:
        balance = btc_position * price
        btc_position = 0.0

final_value = balance if btc_position == 0.0 else btc_position * price
total_return = (final_value / 1000.0 - 1) * 100

# === INVIO EMAIL CON RISULTATO ===

body = f'''
Trading Bot Report - MA50/200 (BTC-USD)

Rendimento finale: {total_return:.2f}%

Capitale finale: ${final_value:.2f}
Capitale iniziale: $1000.00
'''

msg = MIMEMultipart()
msg["From"] = "a.bianco93@icloud.com"
msg["To"] = "a.bianco93@icloud.com"
msg["Subject"] = "Trading Bot - Risultato Giornaliero"
msg.attach(MIMEText(body, "plain"))

try:
    print("Invio email a a.bianco93@icloud.com...")

    with smtplib.SMTP("smtp.mail.me.com", 587) as server:
        server.starttls()
        server.login("a.bianco93@icloud.com", "zeaw-pllb-qrxy-npol")
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())

    print("Email inviata con successo.")
except Exception as e:
    print("Errore nell'invio email:", e)
