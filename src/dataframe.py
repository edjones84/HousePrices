from pandas import DataFrame
from dataclasses import dataclass


@dataclass
class InputDataFrame:
    """This is used to create the output ds and y dataframes to then be used in the neuralprophet modelling
        Parameters
        ----------
            df : pd.DataFrame, dict
                dataframe or dict of dataframes containing column ``ds``, ``y`` with all data
            column names: hpi_global_column, hpi_regional_column,price_regional_column,price_global_column,month column
            ,prophet_month_column and prophet_value column

            N.B column names are defaulted

        Returns
        -------
        all the methods have the same return of a pd.DataFrame
        dataframe or dict of dataframes containing column ``ds``, ``y`` with all data"""

    dataframe: DataFrame
    hpi_global_column: str = "HPI_global"
    hpi_regional_column: str = "HPI_regional"
    price_regional_column: str = "average_price_regional"
    price_global_column: str = "average_price_global"
    month_column: str = "month"
    prophet_month_column: str = "ds"
    prophet_value_column: str = "y"

    def renamed_df(self) -> DataFrame:
        return self.dataframe.rename(columns={self.month_column: self.prophet_month_column})

    def get_region(self) -> str:
        return self.dataframe["region"].iloc[0]


def dataframe_out(dataframe: InputDataFrame, y_column: str) -> DataFrame:
    """specify the column you want as the values from the list:
        HPI_global,HPI_regional,average_price_regional,average_price_global"""
    allowed_list = ["HPI_global", "HPI_regional", "average_price_regional", "average_price_global"]
    if y_column not in allowed_list:
        ValueError(f"y_column must be one of the following: {allowed_list} ")
    df = dataframe.renamed_df()[[dataframe.prophet_month_column, y_column]]
    return df.rename(columns={y_column: dataframe.prophet_value_column})
