import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Dict, List, Union

import pandas as pd
import pandas_ta as ta
import requests

from exceptions import (APIResponseError, APIStatusCodeError, DataError,
                        ExchangeError, IndicatorDataError, TelegramError)
from exchange import (Binance, BINANCE_API_KEY, BINANCE_PRIVATE_KEY,
                      BINANCE_MARKET_TYPE, DATA_MARKET_ID, DATA_TIMEFRAME,
                      DATA_LIMIT, DATA_RETRY_TIME, ORDER_SIZE)
from settings import (BASE_DIR, RSI_PERIOD, RSI_LOWER, RSI_UPPER,
                      TELEGRAM_CHAT_ID, TELEGRAM_ENDPOINT, TELEGRAM_TOKEN,
                      TELEGRAM_MESSAGE)


def check_tokens() -> bool:
    """Проверяет наличие всех переменных окружения."""
    return all((
        BINANCE_API_KEY,
        BINANCE_PRIVATE_KEY,
        BINANCE_MARKET_TYPE,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ))


def get_position(exchange: Binance) -> List[Dict[str, Union[int, float, str]]]:
    """Делает запрос к API биржы и возвращает информацию о позиции."""
    try:
        logging.info('Position request %s', DATA_MARKET_ID)
        response = exchange.fapiPrivate_get_positionrisk(params={'symbol': DATA_MARKET_ID})
    except Binance.error as exc:
        raise ExchangeError(f'Getting position error: {exc}') from exc
    else:
        return response


def check_position_response(
        response: List[Dict[str, Union[int, float, str]]]
) -> Dict[Union[float, str], Dict[str, Union[float, str]]]:
    """Проверяет наличие всех ключей в ответе API биржы."""
    logging.info('Checking the API Response')

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


def get_data(exchange: Binance) -> pd.DataFrame:
    """Делает запрос к API биржы и возвращает данные по инструменту."""
    try:
        logging.info('Request data for a %s', DATA_MARKET_ID)
        response = exchange.fetch_ohlcv(DATA_MARKET_ID, timeframe=DATA_TIMEFRAME, limit=DATA_LIMIT)
    except Binance.error as exc:
        raise ExchangeError(f'Getting position error: {exc}') from exc
    try:
        data = pd.DataFrame(response, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        data = data.iloc[:-1, :]
        data['date'] = pd.to_datetime(data['date'], unit='ms')
    except DataError:
        raise Exception
    else:
        return data


def indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Расчитывает значения индикаторов из данных биржи."""
    try:
        logging.info('Calculation of the value of indicators')
        data = pd.DataFrame()
        data['date'] = df['date']
        data['close'] = df['close'].round(2)
        data['high'] = df['high'].round(2)
        data['low'] = df['low'].round(2)
        data['rsi'] = ta.rsi(df['close'], length=RSI_PERIOD).round(2)
    except Exception as exc:
        raise IndicatorDataError(f'Indicator data conversion error: {exc}') from exc
    else:
        return data


def transaction_decision(indicators_data, position):
    rsi = indicators_data['rsi'].iloc[-1]
    rsi_prev = indicators_data['rsi'].iloc[-2]

    buy = (rsi > RSI_LOWER >= rsi_prev)
    sell = (rsi < RSI_UPPER <= rsi_prev)

    if buy and position <= 0:
        new_order(Binance.run, 'BUY', position)

    if sell and position >= 0:
        new_order(Binance.run, 'SELL', position)


def new_order(exchange, direction: str, amount: float) -> None:
    """Делает запрос к API биржы и выставляет рыночную заявку."""
    diff_amount = abs(float(amount)) + ORDER_SIZE
    print(f'Submitting a market order: {direction}, размер заявки {diff_amount}')

    if direction == "BUY":
        exchange.create_order(symbol=DATA_MARKET_ID, type='MARKET', side='BUY', amount=diff_amount)
    if direction == "SELL":
        exchange.create_order(symbol=DATA_MARKET_ID, type='MARKET', side='SELL', amount=diff_amount)

    send_message(f'*** Submitting a market order: {direction}, size {diff_amount} ***')


def send_message(message: str) -> None:
    """Отправляет сообщение в телеграм."""
    data = {
        'url': TELEGRAM_ENDPOINT.format(token=TELEGRAM_TOKEN),
        'data': {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'markdown',
        },
    }
    try:
        print(f'Sending a message to telegram: {message}')
        logging.info('Sending a message to telegram: %s', message)
        response = requests.post(**data)
        if response.status_code != HTTPStatus.OK:
            raise APIStatusCodeError(
                'Invalid server response: '
                f'http code = {response.status_code}; '
                f'reason = {response.reason}; '
                f'content = {response.text}'
            )
    except Exception as exc:
        raise TelegramError(
            f'Error sending message to telegram: {exc}'
        ) from exc
    else:
        print('Telegram message sent successfully')
        logging.info('Telegram message sent successfully')


def main():
    if not check_tokens():
        error_message = (
            f'Missing required environment variables: '
            'BINANCE_API_KEY, BINANCE_PRIVATE_KEY, BINANCE_MARKET_TYPE, '
            'TELEGRAM_TOKEN, TELEGRAM_CHAT_ID. '
            'The program was stopped'
        )
        send_message(error_message)
        logging.critical(error_message)
        sys.exit(error_message)

    current_position = None
    prev_position = current_position

    while True:
        try:
            response = get_position(Binance().run())
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
                    'No position updates for the %s', DATA_MARKET_ID
                )

        except Exception as exc:
            error_message = f'Program crash: {exc}'
            current_position = error_message
            logging.exception(error_message)

        try:
            if current_position != prev_position:
                send_message(current_position)
                prev_position = current_position
        except TelegramError as exc:
            error_message = f'Program crash: {exc}'
            logging.exception(error_message)

        data = get_data(Binance().run())
        indicators_data = indicators(data)
        transaction_decision(indicators_data, pos)

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
