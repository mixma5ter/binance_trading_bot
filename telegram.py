import requests


class Telegram:
    """Класс телеграм бота."""

    def __init__(self, data):
        self.chat_id = data.get('chat_id')
        self.endpoint = data.get('endpoint')
        self.token = data.get('token')
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
