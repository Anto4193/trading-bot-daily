import os
import time
import logging
import smtplib
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
from email.mime.text import MIMEText

# ==============================
# CONFIGURAZIONE LOGGING
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==============================
# CONFIGURAZIONE API BINANCE TESTNET
# ==============================
API_KEY = os.getenv("BINANCE_API_KEY", "D6Z9qe2RABCGqVpsmrcjnpnqHnjZ0JnQd5GqhUeASgiLfjmtXnG2wPpOimxNhUGi")
API_SECRET = os.getenv("BINANCE_API_SECRET", "J0BNDBqWzwfbboYsUXxSEsCs2SERvXNKlQgmV7lOqPRI3vkTKczLzx4e1YGDRYfx")
client = Client(API_KEY, API_SECRET, testnet=True)

# ==============================
# EMAIL CONFIG
# ==============================
EMAIL_SENDER = "railway.bot.report@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASS", "password")  # Imposta password app Gmail
EMAIL_RECEIVER = "a.bianco93@icloud.com"

# ==============================
# VARIABILI STATO
# ==============================
last_action = None  # "BUY", "SELL", "NONE"
initial_balance = None

# ==============================
# FUNZIONE INVIO EMAIL
# ==============================
def send_email(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        logging.info("📧 Email inviata con successo")
    except Exception as e:
        logging.error(f"Errore invio email: {e}")

# ==============================
# FUNZIONE SALDO TOTALE USDT
# ==============================
def get_total_balance():
    try:
        balances = client.get_account()['balances']
        usdt = next((float(b['free']) for b in balances if b['asset'] == 'USDT'), 0)
        btc = next((float(b['free']) for b in balances if b['asset'] == 'BTC'), 0)
        btc_price = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
        total = usdt + (btc * btc_price)
        return total
    except Exception as e:
        logging.error(f"Errore saldo: {e}")
        return 0

# ==============================
# FUNZIONE STRATEGIA
# ==============================
def moving_average_strategy(symbol="BTCUSDT", qty=0.001):
    global last_action
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=50)
        closes = [float(x[4]) for x in klines]

        fast_ma = sum(closes[-10:]) / 10
        slow_ma = sum(closes) / 50
        current_price = closes[-1]

        logging.info(f"📊 Prezzo: {current_price} | Fast MA: {fast_ma} | Slow MA: {slow_ma}")

        # BUY condition
        if fast_ma > slow_ma * 1.001 and last_action != "BUY":
            try:
                client.order_market_buy(symbol=symbol, quantity=qty)
                last_action = "BUY"
                logging.info("✅ Ordine BUY eseguito.")
            except BinanceAPIException as e:
                logging.error(f"Errore ordine BUY: {e.message}")

        # SELL condition
        elif fast_ma < slow_ma * 0.999 and last_action != "SELL":
            try:
                client.order_market_sell(symbol=symbol, quantity=qty)
                last_action = "SELL"
                logging.info("✅ Ordine SELL eseguito.")
            except BinanceAPIException as e:
                logging.error(f"Errore ordine SELL: {e.message}")
    except Exception as e:
        logging.error(f"⚠️ Errore strategia: {e}")

# ==============================
# MAIN LOOP
# ==============================
if __name__ == "__main__":
    try:
        client.get_account()
        logging.info("✅ Connessione API Testnet riuscita - Account attivo.")
    except BinanceAPIException as e:
        logging.error(f"🚫 Arresto script: {e.message}")
        exit()

    initial_balance = get_total_balance()
    logging.info(f"💰 Saldo iniziale: {initial_balance:.2f} USDT")

    while True:
        moving_average_strategy()
        time.sleep(60)

        # Report giornaliero alle 00:00 UTC
        if datetime.utcnow().strftime('%H:%M') == '00:00':
            current_balance = get_total_balance()
            pnl = ((current_balance - initial_balance) / initial_balance) * 100 if initial_balance else 0
            message = f"Saldo iniziale: {initial_balance:.2f} USDT\nSaldo attuale: {current_balance:.2f} USDT\nPnL: {pnl:.2f}%"
            send_email("Report giornaliero Trading Bot", message)
            initial_balance = current_balance

