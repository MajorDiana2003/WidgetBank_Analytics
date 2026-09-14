from typing import Any, Dict, List

from src.services import investment_bank, search_by_phone_numbers, search_p2p_transfers


def test_investment_bank_calculation(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест округления расходов в инвесткопилку с шагом 50"""
    result: float = investment_bank("2026-09", sample_transactions, limit=50)
    assert result == 68.50


def test_search_by_phone_numbers_success(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест корректности работы регулярного выражения для поиска номеров телефонов"""
    result_json: str = search_by_phone_numbers(sample_transactions)
    assert "+7 999 123-45-67" in result_json
    assert "Иван И." not in result_json


def test_search_p2p_transfers_success() -> None:
    """Тест регулярного выражения поиска P2P-переводов физическим лицам"""
    txs = [{"Категория": "Переводы", "Описание": "Иван И."}]
    result_json: str = search_p2p_transfers(txs)
    assert len(result_json) >= 2
