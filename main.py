import logging
import sys
import time
from http import HTTPStatus

import pandas as pd
import pandas_ta as ta
import requests
from ccxt import BaseError

from exceptions import *
from settings import *


def check_tokens() -> bool:
    """Проверяет наличие всех переменных окружения."""
    return all((
        BINANCE_API_KEY,
        BINANCE_PRIVATE_KEY,
        BINANCE_MARKET_TYPE,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ))


def get_position(exchange):
    """Делает запрос к API биржы и возвращает информацию о позиции."""
    try:
        logging.info('Position request %s', MARKET_ID)
        response = exchange.fapiPrivate_get_positionrisk(params={'symbol': MARKET_ID})
    except BaseError as exc:
        raise ExchangeError(f'Getting position error: {exc}') from exc
    else:
        return response


def check_position_response(response):
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


def get_data(exchange):
    """Делает запрос к API биржы и возвращает данные по инструменту."""
    try:
        logging.info('Request data for a %s', MARKET_ID)
        response = exchange.fetch_ohlcv(MARKET_ID, timeframe=TIMEFRAME, limit=LIMIT)
    except BaseError as exc:
        raise ExchangeError(f'Getting position error: {exc}') from exc
    try:
        data = pd.DataFrame(response, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        data = data.iloc[:-1, :]
        data['date'] = pd.to_datetime(data['date'], unit='ms')
    except DataError:
        raise Exception
    else:
        return data


def indicators(df):
    """Расчитывает значения индикаторов из данных биржи."""
    try:
        logging.info('Calculation of the value of indicators')
        data = pd.DataFrame()
        data['date'] = df['date']
        data['close'] = df['close'].round(2)
        data['high'] = df['high'].round(2)
        data['low'] = df['low'].round(2)
        data['rsi'] = ta.rsi(df['close'], length=RSI).round(2)
    except Exception as exc:
        raise IndicatorDataError(f'Indicator data conversion error: {exc}') from exc
    else:
        return data


def new_order(exchange, direction, amount):
    """Делает запрос к API биржы и выставляет рыночную заявку."""
    diff_amount = abs(float(amount)) + ORDER
    print(f'Submitting a market order: {direction}, размер заявки {diff_amount}')

    if direction == "BUY":
        exchange.create_order(symbol=MARKET_ID, type='MARKET', side='BUY', amount=diff_amount)
    if direction == "SELL":
        exchange.create_order(symbol=MARKET_ID, type='MARKET', side='SELL', amount=diff_amount)

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
            response = get_position(exchange)
            position = check_position_response(response)[MARKET_ID]
            pos = float(position['amount'])

            current_position = MESSAGE.format(
                symbol=MARKET_ID,
                amount=position['amount'],
                entry_price=position['entry_price'],
                direction=('LONG' if pos > 0 else 'SHORT')
            )
            if current_position == prev_position:
                logging.debug(
                    'No position updates for the %s', MARKET_ID
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

        data = get_data(exchange)
        indicators_data = indicators(data)

        rsi = indicators_data['rsi'].iloc[-1]
        rsi_prev = indicators_data['rsi'].iloc[-2]

        buy = (rsi > LOWER >= rsi_prev)
        sell = (rsi < UPPER <= rsi_prev)

        if buy and pos <= 0:
            new_order(exchange, 'BUY', pos)

        if sell and pos >= 0:
            new_order(exchange, 'SELL', pos)

        time.sleep(RETRY_TIME)
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
