import datetime

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

from constants import ParamsEnum, PersonInfoEnum


class PensionCalculator:
    """Класс калькулятора выплат пенсий.

    Params:
        contract_data: Датафрейм с информацией о договорах;
        pension_data: Датафрейм с информацией о размере первоначального платежа для каждого договора;
        params: Словарь с параметрами для расчёта.
    """

    def __init__(
        self,
        contract_data: pd.DataFrame,
        pension_data: pd.DataFrame,
        params: dict,
    ) -> None:
        self._user_data = self._create_user_data(contract_data, pension_data)
        self._params = params

        self._indexing_month: dict[int, float] = {1: self._params[ParamsEnum.PENSION_INDEXING_RATE]}

        self._result_df: pd.DataFrame | None = None

    def _create_user_data(self, contract_data: pd.DataFrame, pension_data: pd.DataFrame) -> pd.DataFrame:
        """Создание единого датафрейма с информацией о каждом договоре.

        Args:
            contract_data: Датафрейм с информацией о договорах;
            pension_data: Датафрейм с информацией о размере первоначального платежа для каждого договора.
        Returns:
            Единый датафрейм с информацией о договорах.
        """
        return contract_data.join(
            pension_data,
        ).rename(
            columns={
                PersonInfoEnum.CONTRACT_NUMBER.value: "contract",
                PersonInfoEnum.SEX.value: "sex",
                PersonInfoEnum.DATE_OF_BIRTH.value: "birthdate",
                PersonInfoEnum.PENSION_START_AGE.value: "pension_start",
                PersonInfoEnum.PENSION_START_AMOUNT.value: "pension_amount",
            }
        )

    def _get_last_day_of_month(self, date: pd.Timestamp) -> pd.Timestamp:
        """Преобразование даты в дату с последним днём месяца.

        Args:
            date: Изначальная дата.
        Returns:
            Дату с тем же месяцем и годом, но с последним днём этого месяца.
        """

        if not date.is_month_end:
            date += pd.offsets.MonthEnd()

        return date

    def _calculate_start_date(self, row) -> datetime.date:
        """Расчёт даты начала выплат для каждого договора.

        Args:
            row: Строка датафрейма, которая содержит целостную информацию об одном договоре.
        Returns:
            Дату начала выплат пенсий в соответствии с договором и параметрами.
        """

        on_pension = relativedelta(self._params[ParamsEnum.START_DATE], row.birthdate).years >= row.pension_start
        start_date = self._params[ParamsEnum.START_DATE]
        if not on_pension:
            start_date = self._get_last_day_of_month(row.birthdate + relativedelta(years=row.pension_start))

        return start_date

    def _preprocess_contract_data(self) -> None:
        """Расчёт нужных данных для заполнения графика платежей.

        Для заполнения графика платежей производятся следующие предварительные расчёты:
            1. Рассчитывается дата начала выплат для каждого договора;
            2. Рассчитывается дата достижения каждым клиентом возраста окончания выплаты пенсии.
        """

        self._user_data["start_date"] = self._user_data.apply(
            lambda row: self._calculate_start_date(row),
            axis=1,
        )
        self._user_data["end_date"] = self._user_data.apply(
            lambda row: row.birthdate + relativedelta(years=self._params[ParamsEnum.MAX_AGE.value], days=1),
            axis=1,
        )

    def calculate(self) -> pd.DataFrame:
        """Основной метод расчёта.

        Returns:
            График платежей для каждого договора в виде датафрейма.
        """

        if self._result_df:
            return self._result_df

        self._preprocess_contract_data()

        data: list[dict] = []

        for contract, row in self._user_data.iterrows():
            payment_date = row.start_date
            payment = row.pension_amount

            while payment_date <= row.end_date:
                payment = np.round(
                    payment * (1 + self._indexing_month.get(payment_date.month, 0)),
                    2,
                )

                data.append(
                    {
                        PersonInfoEnum.CONTRACT_NUMBER.value: contract,
                        PersonInfoEnum.DATE_OF_PAYMENT.value: payment_date.date(),
                        PersonInfoEnum.PENSION_AMOUNT.value: payment,
                    }
                )
                payment_date = self._get_last_day_of_month(payment_date + relativedelta(months=1))

        self._result_df = pd.DataFrame(
            data,
        ).sort_values(
            [PersonInfoEnum.DATE_OF_PAYMENT.value, PersonInfoEnum.CONTRACT_NUMBER.value],
        )

        return self._result_df

    def export_to_df(self, name: str = "Результат.xlsx") -> None:
        """Расчёт и экспорт графика платежей в Excel.

        Args:
            name: Имя выходного файла с расширением.
        """
        self.calculate().to_excel(name, index=False)
