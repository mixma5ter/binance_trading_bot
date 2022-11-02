import os

from ccxt import binance, phemex
from dotenv import load_dotenv

load_dotenv()

# Директория для файла логов
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# РАБОЧИЙ ОБЪЕМ ЗАЯВКИ
ORDER = 0.001

# НАСТРОЙКИ ИНДИКАТОРА RSI
RSI = 14
LOWER = 30
UPPER = 100 - LOWER

MARKET_ID = 'BTCUSDT'
TIMEFRAME = '1h'  # m, h; d, w, M
LIMIT = 250  # количество свечей
RETRY_TIME = 10  # задержка в секундах

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_PRIVATE_KEY = os.getenv('BINANCE_PRIVATE_KEY')
BINANCE_MARKET_TYPE = os.getenv('BINANCE_MARKET_TYPE')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_ENDPOINT = 'https://api.telegram.org/bot{token}/sendMessage'
# Шаблон сообщения телеграмм
MESSAGE = '{symbol}, amount: {amount}, entry price: {entry_price}, direction: {direction}'

# НАСТРОЙКИ БИРЖИ
exchange = binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_PRIVATE_KEY,
    'timeout': 10000,  # number in milliseconds
    'enableRateLimit': True,
    'options': {
        # 'spot', 'future', 'margin', 'delivery'
        'defaultType': BINANCE_MARKET_TYPE,
    }
})

# # пример для биржи phemex
#
# exchange = phemex({
#     'apiKey': PHEMEX_API_KEY,
#     'secret': PHEMEX_PRIVATE_KEY,
#     'enableRateLimit': True,
# })
