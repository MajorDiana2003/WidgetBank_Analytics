import json
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd  # type: ignore

from src.external_api import get_currency_rates, get_stock_prices


def test_get_currency_rates_success() -> None:
    """Тест успешного парсинга ответа курсов валют Центробанка."""
    mock_cbr_data = {"Valute": {"USD": {"Value": 90.50, "Nominal": 1.0}, "EUR": {"Value": 100.00, "Nominal": 1.0}}}

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps(mock_cbr_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result: List[Dict[str, Any]] = get_currency_rates(["USD", "EUR"])

        assert len(result) == 2
        assert result[0]["currency"] == "USD"
        assert result[0]["rate"] == 90.50


def test_get_currency_rates_empty_input() -> None:
    """Тест того, что пустой запрос сразу возвращает пустой список."""
    assert get_currency_rates([]) == []


def test_get_stock_prices_success() -> None:
    """Тест извлечения цен акций из DataFrame yfinance."""
    mock_hist = pd.DataFrame({"Close": [150.75]})

    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_hist
        mock_ticker.return_value = mock_instance

        result: List[Dict[str, Any]] = get_stock_prices(["AAPL"])

        assert len(result) == 1
        assert result[0]["stock"] == "AAPL"
        assert result[0]["price"] == 150.75


def test_get_stock_prices_empty_input() -> None:
    """Тест пустого запроса тикеров акций."""
    assert get_stock_prices([]) == []
