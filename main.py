import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Dict, List, Union

import pandas as pd
import pandas_ta as ta

from exceptions import (APIResponseError, APIStatusCodeError, DataError,
                        ExchangeError, IndicatorDataError, TelegramError)
from exchange import Binance, Exchange
from settings import (BASE_DIR, BINANCE_API_KEY, BINANCE_PRIVATE_KEY, BINANCE_MARKET_TYPE,
                      DATA_LIMIT, DATA_MARKET_ID, DATA_RETRY_TIME, DATA_TIMEFRAME, ORDER_SIZE,
                      RSI_PERIOD, RSI_LOWER, RSI_UPPER, TELEGRAM_CHAT_ID, TELEGRAM_ENDPOINT,
                      TELEGRAM_TOKEN, TELEGRAM_MESSAGE)
from telegram import Telegram

telegram_config = {
    'chat_id': TELEGRAM_CHAT_ID,
    'endpoint': TELEGRAM_ENDPOINT,
    'token': TELEGRAM_TOKEN,
}
telegram = Telegram(telegram_config)

exchange_config = {
    'api_key': BINANCE_API_KEY,
    'private_key': BINANCE_PRIVATE_KEY,
    'market_type': BINANCE_MARKET_TYPE,
    'market_id': DATA_MARKET_ID,
    'timeframe': DATA_TIMEFRAME,
    'limit': DATA_LIMIT,
}
exchange = Binance(exchange_config)


def check_position_response(
        response: List[Dict[str, Union[int, float, str]]]
) -> Dict[Union[float, str], Dict[str, Union[float, str]]]:
    """Проверяет наличие всех ключей в ответе API биржы."""

    if not isinstance(response, list):
        raise TypeError(
            f'API response error: response = {response}'
        )

    positions = {}

    for item in response:
        if not isinstance(item, dict):
            raise TypeError(
                'API response error, '
                f'response = {response}'
            )

        symbol = item.get('symbol')
        if symbol is None:
            raise APIResponseError(
                'API response error, '
                f'response = {response}'
            )

        amount = item.get('positionAmt')
        if amount is None:
            raise APIResponseError(
                'API response error, '
                f'response = {response}'
            )

        entry_price = item.get('entryPrice')
        if entry_price is None:
            raise APIResponseError(
                'API response error, '
                f'response = {response}'
            )

        positions[symbol] = {'amount': amount, 'entry_price': entry_price}

    return positions


def rsi(data: List[List], period) -> List[int]:
    """Расчитывает значения индикатора rsi из данных биржи."""
    try:
        logging.info('Calculation of the value of indicators')
        data = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        data = data.iloc[:-1, :]
        data['date'] = pd.to_datetime(data['date'], unit='ms')
        data['rsi'] = ta.rsi(data['close'], length=period).round(2)
        data = data.dropna()
        rsi_data_list = data['rsi'].tolist()
    except Exception as exc:
        raise IndicatorDataError(f'Indicator data conversion error: {exc}') from exc
    else:
        return rsi_data_list


def transaction_decision(exchange: Exchange, indicators_data: List[int], position: float) -> None:
    """Основная логика для выставления заявки."""
    current_value = indicators_data[-1]
    previous_value = indicators_data[-2]

    buy = (current_value > RSI_LOWER >= previous_value)
    sell = (current_value < RSI_UPPER <= previous_value)

    if buy and position <= 0:
        new_order(exchange, 'BUY', position)

    if sell and position >= 0:
        new_order(exchange, 'SELL', position)


def new_order(exchange: Exchange, direction: str, amount: float) -> None:
    """Рассчитывает объем и выставляет рыночную заявку."""
    diff_amount = abs(float(amount)) + ORDER_SIZE
    print(f'Submitting a market order: {direction}, размер заявки {diff_amount}')

    exchange.create_market_order(direction, amount=diff_amount)

    telegram.send_message(f'*** Submitting a market order: {direction}, size {diff_amount} ***')


def send_message(message: str) -> None:
    """Отправляет сообщение в телеграм."""
    response = telegram.send_message(message)
    if response.status_code != HTTPStatus.OK:
        raise APIStatusCodeError(
            'Invalid server response: '
            f'http code = {response.status_code}; '
            f'reason = {response.reason}; '
            f'content = {response.text}'
        )


def main():
    if not telegram.check_tokens():
        error_message = (
            'Missing required environment variables: '
            'TELEGRAM_CHAT_ID, TELEGRAM_ENDPOINT, TELEGRAM_TOKEN '
            'The program was stopped'
        )
        logging.critical(error_message)
        sys.exit(error_message)

    if not exchange.check_tokens():
        error_message = (
            'Missing required environment variables: '
            'BINANCE_API_KEY, BINANCE_PRIVATE_KEY, BINANCE_MARKET_TYPE '
            'The program was stopped'
        )
        telegram.send_message(error_message)
        logging.critical(error_message)
        sys.exit(error_message)

    current_position = None
    prev_position = current_position

    while True:
        try:
            logging.info(f'Position request {DATA_MARKET_ID}')
            response = exchange.get_position()
        except exchange.error as exc:
            raise ExchangeError(f'Getting position error: {exc}') from exc

        try:
            logging.info('Checking the API Response')
            position = check_position_response(response)[DATA_MARKET_ID]
            pos = float(position['amount'])

            current_position = TELEGRAM_MESSAGE.format(
                symbol=DATA_MARKET_ID,
                amount=position['amount'],
                entry_price=position['entry_price'],
                direction=('LONG' if pos > 0 else 'SHORT')
            )
            if current_position == prev_position:
                logging.debug(
                    f'No position updates for the {DATA_MARKET_ID}'
                )
        except Exception as exc:
            error_message = f'Program crash: {exc}'
            current_position = error_message
            logging.exception(error_message)

        try:
            if current_position != prev_position:
                telegram.send_message(current_position)
                prev_position = current_position
        except TelegramError as exc:
            error_message = f'Program crash: {exc}'
            logging.exception(error_message)

        try:
            logging.info(f'Request data for a {DATA_MARKET_ID}')
            data = exchange.get_data()
        except exchange.error as exc:
            raise DataError(f'Getting data error: {exc}') from exc

        indicator_data = rsi(data, RSI_PERIOD)
        transaction_decision(exchange, indicator_data, pos)

        time.sleep(DATA_RETRY_TIME)
        os.system('cls||clear')


if __name__ == '__main__':
    log_format = (
        '%(asctime)s [%(levelname)s] - '
        '(%(filename)s).%(funcName)s:%(lineno)d - %(message)s'
    )
    log_file = os.path.join(BASE_DIR, 'output.log')
    log_stream = sys.stdout
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(log_stream)
        ]
    )

    main()
