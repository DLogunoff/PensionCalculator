from enum import Enum


class PageEnum(str, Enum):
    """Названия страниц во входном Excel."""

    CONTRACTS_PAGE: str = "Договоры участников"
    PENSION_PAGE: str = "Суммы пенсий"
    PARAMS_PAGE: str = "Параметры расчета"


class PersonInfoEnum(str, Enum):
    """Названия столбцов на страницах с информацией о договорах."""

    CONTRACT_NUMBER: str = "Номер договора"
    SEX: str = "Пол участника"
    DATE_OF_BIRTH: str = "Дата рождения участника"
    PENSION_START_AGE: str = "Пенсионный возраст"
    PENSION_START_AMOUNT: str = "Установленный размер пенсии"

    DATE_OF_PAYMENT: str = "Дата платежа"
    PENSION_AMOUNT: str = "Размер пенсии"


class ParamsEnum(str, Enum):
    """Названия параметров для расчёта."""

    START_DATE: str = "Отчетная дата"
    PENSION_INDEXING_RATE: str = "Ставка индексации пенсии"
    MAX_AGE: str = "Максимальный возраст, лет"
