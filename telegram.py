import requests

from settings import TELEGRAM_CHAT_ID, TELEGRAM_ENDPOINT, TELEGRAM_TOKEN


class Telegram:
    """Класс телеграм бота."""

    def __init__(self):
        self.chat_id = TELEGRAM_CHAT_ID
        self.endpoint = TELEGRAM_ENDPOINT
        self.token = TELEGRAM_TOKEN
        self.message = ''
        self.data = {}

    def check_tokens(self):
        """Проверяет наличие всех переменных окружения."""
        return all((
            self.chat_id,
            self.endpoint,
            self.token,
        ))

    def send_message(self, message):
        """Отправляет сообщение в телеграм."""
        self.message = message
        self.data = {
            'url': self.endpoint.format(token=self.token),
            'data': {
                'chat_id': self.chat_id,
                'text': self.message,
                'parse_mode': 'markdown',
            },
        }
        requests.post(**self.data)
