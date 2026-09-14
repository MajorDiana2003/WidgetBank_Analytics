import functools
import logging
import os
from datetime import datetime
from typing import Any, Callable, Optional, TypeVar, cast

import pandas as pd  # type: ignore

logger = logging.getLogger(__name__)

REPORTS_DIR: str = "data"

F = TypeVar("F", bound=Callable[..., Any])


def save_report_to_file(filename: Optional[str] = None) -> Callable[[F], F]:
    """Декоратор, который записывает результат функции-отчета в файл"""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            logger.info(f"Вызов отчета '{func.__name__}' через декоратор сохранения.")
            result_df: pd.DataFrame = func(*args, **kwargs)

            if filename is None or callable(filename):
                timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_file: str = f"report_{func.__name__}_{timestamp}.xlsx"
            else:

                target_file = filename

            os.makedirs(REPORTS_DIR, exist_ok=True)
            full_path: str = os.path.join(REPORTS_DIR, target_file)

            try:
                if isinstance(result_df, pd.DataFrame):
                    result_df.to_excel(full_path, index=False)
                    logger.info(f"Отчет успешно сохранен в файл {full_path}")
                else:
                    logger.error("Функция вернула объект, не являющийся pd.DataFrame. Файл не сохранен")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета в файл {full_path}: {e}", exc_info=True)

            return result_df

        return cast(F, wrapper)

    if callable(filename):
        func_to_decorate = filename
        filename = None
        return cast(Callable[[F], F], decorator(func_to_decorate))

    return decorator


def _get_three_months_window(df: pd.DataFrame, date_str: Optional[str]) -> pd.DataFrame:
    """Вспомогательная функция для фильтрации расходов за последние 3 месяца от даты"""
    if df.empty:
        return df
    if date_str:
        target_date: pd.Timestamp = pd.to_datetime(date_str, dayfirst=True)
    else:
        target_date = pd.to_datetime(datetime.now())

    start_date: pd.Timestamp = target_date - pd.Timedelta(days=90)

    df_copy: pd.DataFrame = df.copy()
    df_copy["Parsed_Date"] = pd.to_datetime(df_copy["Дата операции"], dayfirst=True)

    filtered_df: pd.DataFrame = df_copy[
        (df_copy["Parsed_Date"] >= start_date)
        & (df_copy["Parsed_Date"] <= target_date)
        & (df_copy["Сумма операции"] < 0)
    ].copy()

    return filtered_df


@save_report_to_file()
def spending_by_category(df: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца"""
    logger.info(f"Формирование отчета расходов для категории: {category}")
    window_df: pd.DataFrame = _get_three_months_window(df, date)
    if window_df.empty:
        return pd.DataFrame()

    category_df: pd.DataFrame = window_df[window_df["Категория"].str.lower() == category.lower()].copy()
    category_df["Сумма операции"] = category_df["Сумма операции"].abs()

    if "Parsed_Date" in category_df.columns:
        category_df.drop(columns=["Parsed_Date"], inplace=True)

    return category_df


@save_report_to_file("weekly_spending_report.xlsx")
def spending_by_day_of_week(df: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает средние траты в каждой из дней недели за последние три месяца"""
    logger.info("Формирование отчета средних расходов по дням недели")
    window_df: pd.DataFrame = _get_three_months_window(df, date)

    if window_df.empty:
        return pd.DataFrame(columns=["День недели", "Сумма операции"])

    window_df["День недели"] = window_df["Parsed_Date"].dt.day_name(locale="ru_RU")
    report_df: pd.DataFrame = window_df.groupby("День недели")["Сумма операции"].mean().abs().round(2).reset_index()
    return report_df


@save_report_to_file()
def spending_workday_vs_weekend(df: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Выводит средние траты в рабочий и в выходной день за последние три месяца"""
    logger.info("Формирование отчета расходов: рабочие против выходных дней")
    window_df: pd.DataFrame = _get_three_months_window(df, date)

    if window_df.empty:
        return pd.DataFrame(columns=["Тип дня", "Сумма операции"])

    window_df["Тип дня"] = window_df["Parsed_Date"].dt.weekday.apply(
        lambda x: "Выходной день" if x >= 5 else "Рабочий день"
    )
    report_df: pd.DataFrame = window_df.groupby("Тип дня")["Сумма операции"].mean().abs().round(2).reset_index()
    return report_df
