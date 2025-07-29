import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from binance.client import Client
from binance.enums import *
import datetime

# === CONFIGURAZIONE ===
API_KEY = "Z41UsiUvJrUiSXZ2cWAXEkyzqscJq5ateXcc9nqkiIl37uIkHpDYmEOPpsjIgMS3"
API_SECRET = "i4Yy3oAaevaZwkyD6w5EviL3zhXqo4lUZRMA0iBc1y3DImpsasAlXFoCzHqZ3G1n"
EMAIL_USER = "a.bianco93@icloud.com"
EMAIL_PASS = "zeaw-pllb-qrxy-npol"

client = Client(API_KEY, API_SECRET, testnet=True)
symbol = "BTCUSDT"
interval = "1h"
quantity = 0.001

# === FUNZIONE STRATEGIA ===
def get_data():
    klines = client.get_klines(symbol=symbol, interval=interval, limit=250)
    df = pd.DataFrame(klines, columns=["time","open","high","low","close","vol","c1","c2","c3","c4","c5","c6"])
    df["close"] = df["close"].astype(float)
    df["MA50"] = df["close"].rolling(window=50).mean()
    df["MA200"] = df["close"].rolling(window=200).mean()
    return df

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP("smtp.mail.me.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())

# === LOGICA TRADING ===
df = get_data()
price = df["close"].iloc[-1]
signal = 1 if df["MA50"].iloc[-1] > df["MA200"].iloc[-1] else 0

open_orders = client.get_open_orders(symbol=symbol)
positions = client.get_account()

btc_balance = float([a for a in positions["balances"] if a["asset"]=="BTC"][0]["free"])
usdt_balance = float([a for a in positions["balances"] if a["asset"]=="USDT"][0]["free"])

message = f"📊 Report Trading Bot\nData: {datetime.datetime.now()}\nPrezzo: {price}\n"

# Se segnale BUY e abbiamo USDT
if signal == 1 and usdt_balance > 10:
    order = client.order_market_buy(symbol=symbol, quantity=quantity)
    buy_price = float(order["fills"][0]["price"])
    sl_price = buy_price * 0.98
    tp_price = buy_price * 1.05
    message += f"🟢 BUY eseguito a {buy_price}\nStop Loss: {sl_price}\nTake Profit: {tp_price}\n"

# Se segnale SELL e abbiamo BTC
elif signal == 0 and btc_balance > 0.0001:
    order = client.order_market_sell(symbol=symbol, quantity=btc_balance)
    sell_price = float(order["fills"][0]["price"])
    message += f"🔴 SELL eseguito a {sell_price}\n"

else:
    message += "⚠️ Nessuna operazione eseguita.\n"

message += f"\nSaldo BTC: {btc_balance}\nSaldo USDT: {usdt_balance}"

send_email("Trading Bot - Report Giornaliero", message)
print("✅ Bot eseguito, email inviata.")

