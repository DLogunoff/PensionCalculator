import pandas as pd

from calculator import PensionCalculator
from constants import PageEnum, PersonInfoEnum


def main():
    input_name = "Данные.xlsx"

    contact_data, pension_data = pd.read_excel(
        input_name,
        sheet_name=[PageEnum.CONTRACTS_PAGE, PageEnum.PENSION_PAGE],
        header=0,
        index_col=PersonInfoEnum.CONTRACT_NUMBER.value,
    ).values()

    params = pd.read_excel(
        input_name,
        sheet_name=PageEnum.PARAMS_PAGE,
        header=None,
        index_col=0,
    ).to_dict()[1]

    calculator = PensionCalculator(
        contact_data,
        pension_data,
        params,
    )

    calculator.export_to_df()


if __name__ == "__main__":
    main()
