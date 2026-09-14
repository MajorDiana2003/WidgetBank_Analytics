import json
import logging
import os
import sys
from typing import Any, Dict, List, cast

import pandas as pd  # type: ignore

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Настраивает базовую конфигурацию логирования для всего проекта"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "project.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )
    logger.info("Логирование успешно инициализировано.")


def load_operations_from_excel(file_path: str) -> list[dict[str, Any]]:
    """
    Считывает финансовые операции из Excel-файла.
    Преобразует NaN значения в стандартные типы
    """
    logger.info(f"Попытка чтения данных из файла: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден по пути: {file_path}")
        return []

    try:

        df: pd.DataFrame = pd.read_excel(file_path)

        df.fillna(
            {"Номер карты": "", "Кэшбэк": 0.0, "Бонусы": 0.0, "Категория": "Неизвестно", "Описание": ""}, inplace=True
        )

        result: List[Dict[str, Any]] = df.to_dict(orient="records")
        logger.info(f"Успешно загружено {len(result)} строк из финансового отчета.")
        return result
    except Exception as e:
        logger.error(f"Критическая ошибка при чтении Excel-файла {file_path}: {e}", exc_info=True)
        return []


def load_user_settings(settings_path: str) -> Dict[str, Any]:
    """
    Загружает пользовательские настройки валют и акций из JSON-файла
    """
    logger.info(f"Загрузка пользовательских настроек из: {settings_path}")

    if not os.path.exists(settings_path):
        logger.warning(f"Файл настроек {settings_path} отсутствует. Возвращаем пустую структуру.")
        return {"user_currencies": [], "user_stocks": []}

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return cast(Dict[str, Any], json.load(f))
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Ошибка при чтении файла настроек {settings_path}: {e}", exc_info=True)
        return {"user_currencies": [], "user_stocks": []}
