import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd  # type: ignore

from src.external_api import get_currency_rates, get_stock_prices
from src.utils import load_user_settings

logger = logging.getLogger(__name__)


def get_greeting(current_time: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток"""
    hour: int = current_time.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def filter_data_by_date_range(df: pd.DataFrame, date_str: str) -> pd.DataFrame:
    """Фильтрует данные с начала месяца по указанную дату включительно"""
    try:
        target_date: datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        start_of_month: datetime = target_date.replace(day=1, hour=0, minute=0, second=0)

        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

        filtered_df: pd.DataFrame = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= target_date)]
        logger.info(
            f"Данные отфильтрованы. Найдено {len(filtered_df)} транзакций за период"
            f"{start_of_month} - {target_date}"
        )
        return filtered_df
    except Exception as e:
        logger.error(f"Ошибка при фильтрации данных по дате: {e}", exc_info=True)
        return pd.DataFrame()


def get_cards_metrics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Собирает метрики по картам: последние 4 цифры, расходы и кешбэк"""
    cards_list: List[Dict[str, Any]] = []

    expenses_df: pd.DataFrame = df[df["Сумма операции"] < 0]
    if expenses_df.empty:
        return cards_list

    grouped_series = expenses_df.groupby("Номер карты")["Сумма операции"].sum()

    for card, total_spent_raw in grouped_series.items():
        card_number: str = str(card).strip()
        if not card_number or card_number == "nan":
            continue

        card_last_4: str = card_number[-4:]

        total_expenses: float = abs(float(total_spent_raw))

        cashback: int = int(total_expenses // 100)

        cards_list.append(
            {
                "last_4": card_last_4,
                "cards_expenses": round(total_expenses, 2),
                "cashback": cashback,
            }
        )
    return cards_list


def get_top_transactions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Возвращает топ-5 транзакций по сумме платежа"""
    top_list: List[Dict[str, Any]] = []
    if df.empty:
        return top_list
    top_df: pd.DataFrame = df.reindex(df["Сумма операции"].abs().sort_values(ascending=False).index).head(5)

    for _, row in top_df.iterrows():

        formatted_date: str = pd.to_datetime(row["Дата операции"]).strftime("%d.%m.%Y")

        top_list.append(
            {
                "date": formatted_date,
                "amount": float(row["Сумма операции"]),
                "category": str(row["Категория"]),
                "description": str(row["Описание"]),
            }
        )
    return top_list


def main_page_view(operations_data: List[Dict[str, Any]], date_str: str, settings_path: str) -> Dict[str, Any]:
    """Главная функция для генерации JSON-ответа страницы 'Главная'"""
    logger.info(f"Начало формирования данных для Главной страницы на дату: {date_str}")

    try:
        current_time: datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logger.error(f"Неверный формат даты {date_str}: {e}")
        current_time = datetime.now()

    greeting: str = get_greeting(current_time)

    df: pd.DataFrame = pd.DataFrame(operations_data)

    if df.empty:
        logger.warning("Передан пустой список операций.")
        filtered_df = df
    else:
        filtered_df = filter_data_by_date_range(df, date_str)

    cards_data: List[Dict[str, Any]] = get_cards_metrics(filtered_df)

    top_transactions: List[Dict[str, Any]] = get_top_transactions(filtered_df)

    settings: Dict[str, Any] = load_user_settings(settings_path)

    user_currencies: List[str] = settings.get("user_currencies", ["USD", "EUR"])
    user_stocks: List[str] = settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

    currency_rates: List[Dict[str, Any]] = get_currency_rates(user_currencies)
    stock_prices: List[Dict[str, Any]] = get_stock_prices(user_stocks)

    response_data: Dict[str, Any] = {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    logger.info("Данные для Главной страницы успешно сформированы.")
    return response_data
