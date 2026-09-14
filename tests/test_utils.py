from typing import Any, Dict, List
from unittest.mock import mock_open, patch

from src.utils import load_operations_from_excel, load_user_settings


def test_load_user_settings_success(sample_user_settings_json: str) -> None:
    """Тест успешного чтения файла настроек JSON"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=sample_user_settings_json)
    ):
        result: Dict[str, Any] = load_user_settings("dummy_path.json")
        assert result["user_currencies"] == ["USD", "EUR"]
        assert result["user_stocks"] == ["AAPL", "TSLA"]


def test_load_user_settings_file_not_found() -> None:
    """Тест поведения системы при отсутствии конфигурационного файла JSON"""
    with patch("os.path.exists", return_value=False):
        result: Dict[str, Any] = load_user_settings("non_existent.json")
        assert result == {"user_currencies": [], "user_stocks": []}


def test_load_operations_from_excel_file_not_found() -> None:
    """Тест поведения чтения Excel, если файл отсутствует"""
    with patch("os.path.exists", return_value=False):
        result: List[Dict[str, Any]] = load_operations_from_excel("missing.xlsx")
        assert result == []
