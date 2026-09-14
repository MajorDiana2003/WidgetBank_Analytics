from datetime import datetime
from typing import Any, Dict, List

import pandas as pd  # type: ignore
import pytest

from src.views import get_cards_metrics, get_greeting, get_top_transactions


@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (8, "Доброе утро"),
        (14, "Добрый день"),
        (19, "Добрый вечер"),
        (2, "Доброй ночи"),
    ],
)
def test_get_greeting_time_zones(hour: int, expected_greeting: str) -> None:
    """Параметризованный тест генерации приветствия по часам суток"""
    test_dt: datetime = datetime(2026, 9, 14, hour, 0, 0)
    assert get_greeting(test_dt) == expected_greeting


def test_get_cards_metrics_calculation() -> None:
    """Тест расчета финансовых показателей по картам"""
    local_txs = [
        {"Номер карты": "4444555566667197", "Сумма операции": -100.0},
        {"Номер карты": "4444555566667197", "Сумма операции": -50.0},
    ]
    df_test = pd.DataFrame(local_txs)
    metrics = get_cards_metrics(df_test)

    assert len(metrics) == 1
    assert metrics[0]["last_4"] == "7197"
    assert metrics[0]["cards_expenses"] == 150.0
    assert metrics[0]["cashback"] == 1


def test_get_top_transactions_sorting(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест определения ТОП-5 транзакций по максимальной сумме платежа"""
    df_test: pd.DataFrame = pd.DataFrame(sample_transactions)
    top_txs: List[Dict[str, Any]] = get_top_transactions(df_test)

    assert len(top_txs) <= 5
    assert top_txs[0]["amount"] == -300.00
    assert top_txs[0]["category"] == "Переводы"
