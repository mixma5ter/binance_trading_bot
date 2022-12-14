# Торговый робот для криптобиржи [![Binance](https://img.shields.io/badge/Binance-FCD535?style=for-the-badge&logo=binance&logoColor=white)](https://www.binance.com)

[![Mixmaster](https://img.shields.io/badge/Developed%20by-mixmaster-blue?style=for-the-badge)](https://github.com/mixma5ter)

Робот основан на торговом индикаторе RSI. При выходе индикатора из области перепроданности, делает покупку. При выходе из области перекупленности, осуществляет продажу.

Все сделки проводятся по рыночной цене на указанный объём заявки.

При первом запуске робот присылает сообщение в телеграм с данными о позиции. Продолжает оповещать в автономном режиме о работе программы и смене позиции.

В программе также реализовано сохранение логов в отдельный файл.

## Технологии

* Python 3.7
* CCXT
* Pandas
* Numpy
* Requests
* Логирование
* Телеграм-бот
* ООП

## ВНИМАНИЕ! Это торговый робот! Вы запускаете его на свой страх и риск!

- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
```bash
pip install -r requirements.txt
``` 
- Настройте параметры подключения в файле `.env`
```
BINANCE_API_KEY - API ключ биржи Binance [https://www.binance.com/ru/support/faq/360002502072]
BINANCE_PRIVATE_KEY - Приватный ключ биржи Binance
BINANCE_MARKET_TYPE - Тип торговый площадки (future или spot)
TELEGRAM_TOKEN - Токен телеграм
TELEGRAM_CHAT_ID - ID телеграм чата
``` 
- Запустите файл `main.py`

## Настройки

Настройки находятся в файле `settings.py`
```
ORDER - рабочий объем заявки
MARKET_ID - торговый инструмент
TIMEFRAME - рабочий таймфрейм
LIMIT - количество свечей
RETRY_TIME - задержка в секундах
PERIOD - длина индикатора
LOWER - граница перепроданности
UPPER - граница перекупленности
```
