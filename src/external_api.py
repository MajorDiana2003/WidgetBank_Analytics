import json
import logging
import urllib.request
from typing import Any, Dict, List, cast

import yfinance as yf  # type: ignore

# Настраиваем логер
logger = logging.getLogger(__name__)


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает курсы валют (USD, EUR) к рублю с помощью встроенной библиотеки urllib"""
    if not currencies:
        logger.warning("Передан пустой список валют для запроса курсов.")
        return []

    logger.info(f"Запрос курсов валют для: {','.join(currencies)}")
    rates_list: List[Dict[str, Any]] = []
    try:
        url = "https://cbr-xml-daily.ru"

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                response_text = response.read().decode("utf-8").strip()

                if not response_text:
                    logger.error("API Центробанка вернуло пустой ответ.")
                    return []
                data = cast(Dict[str, Any], json.loads(response_text))
                valute_data: Dict[str, Any] = data.get("Valute", {})

                for currency in currencies:
                    currency_info: Dict[str, Any] | None = valute_data.get(currency)

                    if currency_info:
                        value: float = float(currency_info.get("Value", 0.0))
                        nominal: float = float(currency_info.get("Nominal", 1.0))

                        if value > 0:
                            actual_rate: float = round(value / nominal, 2)
                            rates_list.append({"currency": currency, "rate": actual_rate})
                            logger.info(f"Успешно получен курс для {currency}: {actual_rate} RUB")
                        else:
                            logger.warning(f"Получена некорректная цена для {currency}.")

                    else:
                        logger.warning(f"Валюта {currency} не найдена в ответе API Центробанка.")

            else:
                logger.error(f"Ошибка API Центробанка. Статус ответа: {response.status}")

    except Exception as e:
        logger.error(f"Сбой при получении курсов валют: {e}")
        return []

    return rates_list


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Получает актуальную стоимость акций в режиме реального времени через yfinance"""
    if not stocks:
        logger.warning("Передан пустой список акций для запроса стоимости.")
        return []

    logger.info(f"Запрос стоимости акций для тикеров: {','.join(stocks)}")
    stocks_list: List[Dict[str, Any]] = []

    for ticker in stocks:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")

            if not hist.empty:
                price: float = float(hist["Close"].iloc[-1])

                if price > 0:
                    actual_price: float = round(price, 2)
                    stocks_list.append({"stock": ticker, "price": actual_price})
                    logger.info(f"Успешно получена цена для акции {ticker}: {actual_price}")
                else:
                    logger.warning(f"Получена некорректная (нулевая или отрицательная) цена для {ticker}.")
            else:
                logger.warning(f"Не удалось получить историю торгов для тикера {ticker} (тикер указан неверно).")

        except Exception as e:
            logger.error(f"Ошибка при обработке тикера {ticker}: {e}", exc_info=True)

    return stocks_list
