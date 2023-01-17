# Trading bot for the cryptocurrency exchange [![Binance](https://img.shields.io/badge/Binance-FCD535?style=for-the-badge&logo=binance&logoColor=white)](https://www.binance.com)

[![Mixmaster](https://img.shields.io/badge/Developed%20by-mixmaster-blue?style=for-the-badge)](https://github.com/mixma5ter)

This is an RSI-based bot. It gets a buy signal when the RSI goes out of the oversold region and a sell signal when the RSI goes out of the overbought region.

All transactions are done at the market price with the size specified.

When first launched the bot sends a message in Telegram with the information on the position. It keeps reporting on the program operation and position changes in standalone mode.

The program also saves its logs in a separate file.

## Tech stack

* Python 3.7
* CCXT
* Pandas
* Numpy
* Requests
* Logging
* Telegram-bot
* OOP

## WARNING! This is a trading bot! Use it at your own risk!

- Create and activate your virtual environment
- Install the dependencies from requirements.txt
```bash
pip install -r requirements.txt
``` 
- Set the connection parameters in the `.env` file
```
BINANCE_API_KEY - API key of the exchange [https://www.binance.com/ru/support/faq/360002502072]
BINANCE_PRIVATE_KEY - Binance private key
BINANCE_MARKET_TYPE - market type (future or spot)
TELEGRAM_TOKEN - Telegram token
TELEGRAM_CHAT_ID - Telegram chat ID
``` 
- Run `main.py`

## Settings

The settings are in `settings.py`
```
ORDER - operational size of the order
MARKET_ID - trading tool
TIMEFRAME - operational timeframe
LIMIT - number of candles
RETRY_TIME - delay time in seconds
PERIOD - indicator’s length
LOWER - oversold limit
UPPER - overbought limit
```
