import os

from dotenv import load_dotenv

load_dotenv()

# ДИРЕКТОРИЯ ДЛЯ ФАЙЛА ЛОГОВ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# НАСТРОЙКИ TELEGRAM
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_ENDPOINT = 'https://api.telegram.org/bot{token}/sendMessage'
# шаблон сообщения телеграмм
TELEGRAM_MESSAGE = '{symbol}, amount: {amount}, entry price: {entry_price}, direction: {direction}'

# НАСТРОЙКИ ИНДИКАТОРА RSI
RSI_PERIOD = 14
RSI_LOWER = 30
RSI_UPPER = 100 - RSI_LOWER
