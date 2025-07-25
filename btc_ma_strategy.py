import yfinance as yf
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

data = yf.download("BTC-USD", start="2020-01-01", end=datetime.today().strftime('%Y-%m-%d'), interval="1d")
data.dropna(inplace=True)

data["MA10"] = data["Close"].rolling(window=10).mean()
data["MA150"] = data["Close"].rolling(window=150).mean()

data["signal"] = 0
data.loc[data["MA10"] > data["MA150"], "signal"] = 1
data["position"] = data["signal"].diff().fillna(0)

initial_balance = 100
balance = initial_balance
btc_position = 0

for i in range(len(data)):
    price = float(data["Close"].iloc[i])
    signal = int(data["position"].iloc[i])

    if signal == 1 and btc_position == 0.0:
        btc_position = balance / price
        balance = 0.0
    elif signal == -1 and btc_position > 0.0:
        balance = btc_position * price
        btc_position = 0.0

final_value = balance if btc_position == 0 else btc_position * float(data["Close"].iloc[-1])
total_return = ((final_value - initial_balance) / initial_balance) * 100
last_price = float(data["Close"].iloc[-1])
last_signal = "BUY" if data["signal"].iloc[-1] == 1 else "SELL"

subject = "📈 Trading Bot – Report Giornaliero"
body = f"Segnale: {last_signal}\nPrezzo BTC: ${last_price:,.2f}\nRendimento cumulato: {total_return:.2f}%"

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = "tradingbot@report.com"
msg["To"] = "a.bianco93@icloud.com"

try:
    with smtplib.SMTP("smtp.mailtrap.io", 587) as server:
        server.login("user", "password")  # Da personalizzare
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
except Exception as e:
    print("Errore nell'invio email:", e)
