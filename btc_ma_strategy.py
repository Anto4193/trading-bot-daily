import os
import time
import logging
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

# === CONFIGURAZIONE ===
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET, testnet=True)

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1HOUR
LOOKBACK_SHORT = 10
LOOKBACK_LONG = 50
TRAILING_STOP_PCT = 0.10
QUANTITY = 0.001  # BTC da acquistare

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def get_data(symbol, interval, limit=100):
    """Scarica i dati storici da Binance."""
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(
        klines,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )
    data["close"] = data["close"].astype(float)
    return data


def trading_loop():
    position_open = False
    entry_price = 0.0
    max_price = 0.0

    while True:
        try:
            df = get_data(SYMBOL, INTERVAL)
            short_ma = df["close"].tail(LOOKBACK_SHORT).mean()
            long_ma = df["close"].tail(LOOKBACK_LONG).mean()
            price = df["close"].iloc[-1]

            # === ENTRATA LONG ===
            if not position_open and short_ma > long_ma:
                client.order_market_buy(symbol=SYMBOL, quantity=QUANTITY)
                entry_price = price
                max_price = price
                position_open = True
                logger.info("Entrata LONG a %.2f", price)

            # === GESTIONE POSIZIONE ===
            elif position_open:
                max_price = max(max_price, price)
                stop_price = max_price * (1 - TRAILING_STOP_PCT)

                if price <= stop_price or short_ma < long_ma:
                    client.order_market_sell(symbol=SYMBOL, quantity=QUANTITY)
                    position_open = False
                    logger.info("Uscita LONG a %.2f", price)

            time.sleep(60)  # evita di saturare l'API

        except BinanceAPIException as e:
            logger.error("Errore API Binance: %s", e)
            time.sleep(60)
        except Exception as e:
            logger.exception("Errore inatteso: %s", e)
            time.sleep(60)


if __name__ == "__main__":
    trading_loop()
