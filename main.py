import json
import logging
import os
from typing import Any, Dict, List

import pandas as pd  # type: ignore

from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import load_operations_from_excel, setup_logging
from src.views import main_page_view

logger = logging.getLogger(__name__)


def main() -> None:
    """Главная управляющая функция приложения"""
    # 1. Запуск логирования
    setup_logging()
    logger.info("Финансовое приложение успешно запущено.")
    print("Инициализация приложения... Проверьте лог-файл.")

    # 2. Определение путей к файлам конфигурации и данных
    root_dir: str = os.path.dirname(os.path.abspath(__file__))
    excel_path: str = os.path.join(root_dir, "data", "operations.xlsx")
    settings_path: str = os.path.join(root_dir, "user_settings.json")

    # 3. Безопасная загрузка транзакций
    logger.info(f"Попытка чтения данных из файла: {excel_path}")
    raw_transactions: List[Dict[str, Any]] = load_operations_from_excel(excel_path)

    if not raw_transactions:
        logger.error("Критическая ошибка: Данные транзакций пусты или файл отсутствует.")
        print("Ошибка: Не удалось загрузить транзакции. Проверьте логи в app.log.")
        return

    logger.info(f"Успешно загружено {len(raw_transactions)} записей транзакций.")
    print(f"Данные успешно загружены. Найдено операций: {len(raw_transactions)}")

    # 4. Демонстрация: Генерация Веб-страницы "Главная"
    print("\n" + "=" * 10 + "4. Демонстрация: Генерация Веб-страницы 'Главная' " + "=" * 10)
    print("1. Тест: Генерация страницы 'Главная'")

    test_date_str: str = "2020-05-20 14:30:00"

    main_page_json: Dict[str, Any] = main_page_view(
        operations_data=raw_transactions, date_str=test_date_str, settings_path=settings_path
    )

    json_output: str = json.dumps(main_page_json, ensure_ascii=False, indent=4)
    print("Итоговый JSON-ответ для фронтенда (первые 500 символов):")
    print(json_output[:500] + "\n... [Данные обрезаны для удобства вывода]")

    # 5. Демонстрация: Работа Сервиса "Инвесткопилка"
    print("\n" + "=" * 10 + " 5. Демонстрация: Работа Сервиса 'Инвесткопилка' " + "=" * 10)
    print("2. Тест: Расчет сервиса 'Инвесткопилка'")

    test_month: str = "2020-05"
    test_limit: int = 50

    savings: float = investment_bank(month=test_month, transactions=raw_transactions, limit=test_limit)
    print(f"За месяц {test_month} при округлении до {test_limit} руб. накоплено: {savings} руб.")

    # 6. Демонстрация: Формирование Excel-отчетов
    print("\n" + "=" * 10 + " 6. Демонстрация: Формирование Excel-отчетов " + "=" * 10)
    print("3. Тест: Формирование отчета по категориям")

    test_category: str = "Супермаркеты"
    test_report_date: str = "20.05.2020"

    df_for_reports = pd.DataFrame(raw_transactions)
    report_df: pd.DataFrame = spending_by_category(df_for_reports, test_category, test_report_date)
    print("Отчет успешно сформирован и записан в файл.")
    print(f"Найдено расходов в категории '{test_category}' за 3 месяца: {len(report_df)}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
