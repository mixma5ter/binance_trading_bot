from abc import ABC

from ccxt import BaseError, binance, phemex


class Exchange(ABC):
    """Абстрактный класс биржи."""

    def __init__(self, data):
        self.api_key = data.get('api_key')
        self.private_key = data.get('private_key')
        self.market_type = data.get('market_type')
        self.market_id = data.get('market_id')
        self.timeframe = data.get('timeframe')
        self.limit = data.get('limit')
        self.exchange_config = None
        self.exchange = None
        self.error = BaseError

    def check_tokens(self):
        """Проверяет наличие всех переменных окружения."""
        return all((
            self.api_key,
            self.private_key,
            self.market_type,
        ))

    def get_position(self):
        """Делает запрос к API биржы и возвращает информацию о позиции."""
        response = self.exchange.fapiPrivate_get_positionrisk(
            params={'symbol': self.market_id}
        )
        return response

    def get_data(self):
        """Делает запрос к API биржы и возвращает данные по инструменту."""
        response = self.exchange.fetch_ohlcv(
            self.market_id,
            timeframe=self.timeframe,
            limit=self.limit
        )
        return response

    def create_market_order(self, side, amount):
        self.exchange.create_order(symbol=self.market_id, type='MARKET', side=side, amount=amount)


class Binance(Exchange):
    """Класс биржи Binance."""

    def __init__(self, data):
        super().__init__(data)
        self.exchange_config = {
            'apiKey': self.api_key,
            'secret': self.private_key,
            'timeout': 10000,
            'enableRateLimit': True,
            'options': {'defaultType': self.market_type, }
        }
        self.exchange = binance(self.exchange_config)


class Phemex(Exchange):
    """Класс биржи Phemex."""

    def __init__(self, data):
        super().__init__(data)
        self.exchange_config = {
            'apiKey': self.api_key,
            'secret': self.private_key,
            'enableRateLimit': True
        }
        self.exchange = phemex(self.exchange_config)
