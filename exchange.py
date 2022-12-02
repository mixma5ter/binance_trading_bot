from ccxt import BaseError, binance, phemex

from settings import (BINANCE_API_KEY, BINANCE_PRIVATE_KEY, BINANCE_MARKET_TYPE,
                      DATA_MARKET_ID, DATA_LIMIT, DATA_TIMEFRAME)


class Exchange:
    """Основной класс биржи."""
    def __init__(self):
        self.api_key = None
        self.private_key = None
        self.market_type = None
        self.market_id = DATA_MARKET_ID
        self.timeframe = DATA_TIMEFRAME
        self.limit = DATA_LIMIT
        self.exchange_config = {}
        self.exchange = binance(self.exchange_config)
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

    def __init__(self):
        super().__init__()
        self.api_key = BINANCE_API_KEY
        self.private_key = BINANCE_PRIVATE_KEY
        self.market_type = BINANCE_MARKET_TYPE
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

    def __init__(self):
        super().__init__()
        self.api_key = 'PHEMEX_API_KEY'
        self.private_key = 'PHEMEX_PRIVATE_KEY'
        self.exchange_config = {
            'apiKey': self.api_key,
            'secret': self.private_key,
            'enableRateLimit': True
        }
        self.exchange = phemex(self.exchange_config)
