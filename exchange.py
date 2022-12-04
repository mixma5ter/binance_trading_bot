from abc import ABC
from typing import Dict, List

import numpy as np
from ccxt import BaseError, binance, phemex


class DataTransferObject(Dict):
    """Контейнер данных."""

    date: List[str]
    open: List[float]
    high: List[float]
    low: List[float]
    close: List[float]
    volume: List[float]
    indicators: List[Dict[str, List[float]]]


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
        data = np.array(response)
        data = data.transpose()

        return DataTransferObject(
            date=data[0].astype(str),
            open=data[1].astype(float),
            high=data[2].astype(float),
            low=data[3].astype(float),
            close=data[4].astype(float),
            volume=data[5].astype(float),
            indicators=[],
        )

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
