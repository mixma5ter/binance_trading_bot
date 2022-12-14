import os

from dotenv import load_dotenv

load_dotenv()

# ДИРЕКТОРИЯ ДЛЯ ФАЙЛА ЛОГОВ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# РАБОЧИЙ ОБЪЕМ ЗАЯВКИ
ORDER_SIZE = 0.001

# НАСТРОЙКИ БИРЖИ
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_PRIVATE_KEY = os.getenv('BINANCE_PRIVATE_KEY')
BINANCE_MARKET_TYPE = os.getenv('BINANCE_MARKET_TYPE')

# НАСТРОЙКИ ТОРГОВОГО ИНСТРУМЕНТА
DATA_MARKET_ID = 'BTCUSDT'
DATA_TIMEFRAME = '1h'  # m, h; d, w, M
DATA_LIMIT = 250  # количество свечей
DATA_RETRY_TIME = 10  # задержка в секундах

# НАСТРОЙКИ ИНДИКАТОРА RSI
RSI_PERIOD = 14
RSI_LOWER = 30
RSI_UPPER = 100 - RSI_LOWER

# НАСТРОЙКИ TELEGRAM
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_ENDPOINT = 'https://api.telegram.org/bot{token}/sendMessage'
# шаблон сообщения телеграмм
TELEGRAM_MESSAGE = '{symbol}, amount: {amount}, entry price: {entry_price}, direction: {direction}'
