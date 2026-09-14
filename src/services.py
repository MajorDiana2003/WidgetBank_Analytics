import json
import logging
import math
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Рассчитывает сумму округления расходов в 'Инвесткопилку' за указанный месяц"""
    logger.info(f"Старт расчета инвесткопилки за месяц {month} с шагом округления {limit} руб.")
    total_savings: float = 0.0

    monthly_txs: List[Dict[str, Any]] = [
        tx
        for tx in transactions
        if str(tx.get("Дата операции", "")).startswith(month)
        or (
            len(str(tx.get("Дата операции", "")).split(".")) >= 3
            and f"{str(tx.get('Дата операции', '')).split('.')[2][:4]}-"
            f"{str(tx.get('Дата операции', '')).split('.')[1]}" == month
        )
    ]

    for tx in monthly_txs:
        try:
            amount: float = float(tx.get("Сумма операции", 0.0))

            if amount >= 0:
                continue

            abs_amount: float = abs(amount)

            if abs_amount % limit == 0:
                continue

            rounded_amount: float = float(math.ceil(abs_amount / limit) * limit)
            savings: float = rounded_amount - abs_amount
            total_savings += savings
        except (ValueError, TypeError) as e:
            logger.error(f"Ошибка конвертации суммы в транзакциях: {e}")
            continue

    logger.info(f"Расчет инвесткопилки завершен. Накоплено: {round(total_savings, 2)} руб.")
    return round(total_savings, 2)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> str:
    """Ищет транзакции по подстроке в описании или категории без учета регистра"""
    logger.info(f"Старт простого поиска по подстроке: '{query}'")
    query_lower: str = query.lower()

    filtered_txs: List[Dict[str, Any]] = list(
        filter(
            lambda tx: query_lower in str(tx.get("Описание", "")).lower()
            or query_lower in str(tx.get("Категория", "")).lower(),
            transactions,
        )
    )

    logger.info(f"Поиска завершен. Найдено подходящих транзакций: {len(filtered_txs)}")
    return json.dumps(filtered_txs, ensure_ascii=False, indent=4)


def search_by_phone_numbers(transactions: List[Dict[str, Any]]) -> str:
    """Ищет транзакции, содержащие российские мобильные номера телефонов в описании"""
    logger.info("Старт поиска транзакций, содержащих номера телефонов")

    phone_pattern = re.compile(r"(\+7|8)\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}")

    filtered_txs: List[Dict[str, Any]] = [
        tx for tx in transactions if phone_pattern.search(str(tx.get("Описание", "")))
    ]

    logger.info(f"Поиск по телефонным номерам завершен. Найдено: {len(filtered_txs)}")
    return json.dumps(filtered_txs, ensure_ascii=False, indent=4)


def search_p2p_transfers(transactions: List[Dict[str, Any]]) -> str:
    """Ищет переводы физическим лицам"""
    logger.info("Старт поиска исходящих P2P переводов физическим лицам")

    p2p_pattern = re.compile(r"[А-ЯЁ][а-яё]+\s[А=ЯЁ]\.")

    filtered_txs: List[Dict[str, Any]] = [
        tx
        for tx in transactions
        if str(tx.get("Категория", "")).strip() == "Переводы"
        and p2p_pattern.search(str(tx.get("Описание", "")).strip())
    ]

    logger.info(f"Поиск P2P переводов завершен. Найдено операций: {len(filtered_txs)}")
    return json.dumps(filtered_txs, ensure_ascii=False, indent=4)
