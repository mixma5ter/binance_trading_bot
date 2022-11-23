import os

from ccxt import BaseError, binance, Exchange, phemex
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_PRIVATE_KEY = os.getenv('BINANCE_PRIVATE_KEY')
BINANCE_MARKET_TYPE = os.getenv('BINANCE_MARKET_TYPE')


class Binance(Exchange):
    """Настройки биржи Binance."""

    def __init__(self, set_exc):
        super().__init__()
        self.set_exc = set_exc
        self.exchange = binance(self.set_exc)

    def error(self):
        return BaseError


binance_settings = {
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_PRIVATE_KEY,
    'timeout': 10000,
    'enableRateLimit': True,
    'options': {'defaultType': BINANCE_MARKET_TYPE, }
}

# пример для биржи phemex
phemex_settings = phemex({
    'apiKey': 'PHEMEX_API_KEY',
    'secret': 'PHEMEX_PRIVATE_KEY',
    'enableRateLimit': True
})

exchange = Binance(binance_settings)
