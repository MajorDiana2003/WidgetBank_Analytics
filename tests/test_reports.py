from typing import Any, Dict, List
from unittest.mock import patch

import pandas as pd  # type: ignore

from src.reports import _get_three_months_window, spending_by_category  # type: ignore


def test_get_three_months_window_filtration() -> None:
    """Тест того, что вспомогательная функция отчетов правильно отсекает старые траты"""
    test_data: List[Dict[str, Any]] = [
        {"Дата операции": "14.09.2026 12:00:00", "Сумма операции": -100.0, "Категория": "Продукты"},
        {"Дата операции": "14.01.2026 12:00:00", "Сумма операции": -500.0, "Категория": "Продукты"},
        {"Дата операции": "15.09.2026 12:00:00", "Сумма операции": 2000.0, "Категория": "Зарплата"},
    ]

    df_test = pd.DataFrame(test_data)
    result_df: pd.DataFrame = _get_three_months_window(df_test, "14.09.2026 23:59:59")

    assert len(result_df) == 1
    assert float(result_df["Сумма операции"].iloc[0]) == -100.0


def test_spending_by_category_report(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест отчета по категориям"""
    with patch("pandas.DataFrame.to_excel") as mock_to_excel:
        df_transactions = pd.DataFrame(sample_transactions)
        report_df: pd.DataFrame = spending_by_category(df_transactions, "Супермаркеты", "14.09.2026 23:59:59")

        assert len(report_df) == 1
        assert float(report_df["Сумма операции"].iloc[0]) == 171.50

        mock_to_excel.assert_called_once()
