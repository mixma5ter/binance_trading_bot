import os

from ccxt import BaseError, binance
from dotenv import load_dotenv

load_dotenv()

# НАСТРОЙКИ БИРЖИ
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_PRIVATE_KEY = os.getenv('BINANCE_PRIVATE_KEY')
BINANCE_MARKET_TYPE = os.getenv('BINANCE_MARKET_TYPE')

# РАБОЧИЙ ОБЪЕМ ЗАЯВКИ
ORDER_SIZE = 0.001

# НАСТРОЙКИ ТОРГОВОГО ИНСТРУМЕНТА
DATA_MARKET_ID = 'BTCUSDT'
DATA_TIMEFRAME = '1h'  # m, h; d, w, M
DATA_LIMIT = 250  # количество свечей
DATA_RETRY_TIME = 10  # задержка в секундах


class Binance(binance):
    def __init__(self):
        super().__init__()
        self.set_exc = {}
        self.binance = binance
        self.error = BaseError

    def run(self):
        self.set_exc = {
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_PRIVATE_KEY,
            'timeout': 10000,
            'enableRateLimit': True,
            'options': {'defaultType': BINANCE_MARKET_TYPE, }
        }
        self.binance = binance(self.set_exc)
        return self.binance

    def error(self):
        return self.error
