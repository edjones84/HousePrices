import os

import pandas as pd
from neuralprophet import NeuralProphet
from pandas import DataFrame

from src.dataframe import InputDataFrame, dataframe_out

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


def forecaster(dataframe: DataFrame) -> DataFrame:
    """This uses neural prophet https://github.com/ourownstory/neural_prophet to model the future house price data for both
    raw prices and the HPI (house price index) 10 years in the future
                Parameters @param
                ----------
                    dataframe : pd.Dataframe
                        dataframe or dict of dataframes containing column ``ds``, ``y``
                Returns
                -------
                    dataframe : pd.Dataframe
                        dataframe or dict of dataframes containing column ``ds``, ``y`` and ``yhat1``  """
    m = NeuralProphet()
    df_fit = m.fit(dataframe, "M")
    # 5 years in the future
    df_future = m.make_future_dataframe(dataframe, periods=5 * 12)
    forecast = m.predict(df=df_future)
    dataframe['ythat'] = None
    forecast_df = forecast[['ds', 'y', 'yhat1']]
    final_df = pd.concat([dataframe, forecast_df]).reset_index(drop=True)
    return final_df


def apply(dataframe: InputDataFrame) -> dict:
    """applys the forecaster to all the relevant inputs
            Parameters @param
            ----------
                df : InputDataFrame()
                    dataframe or dict of dataframes containing column ``ds``, ``y`` with all data
                column names: hpi_global_column, hpi_regional_column,price_regional_column,price_global_column,month column
                ,prophet_month_column and prophet_value column

                N.B column names are defaulted

            Returns
            -------
            returns a dictionary of 4 dataframes for HPI global and regional and the raw prices global
            and regional and the actual region"""

    return {"hpi_regional_df": forecaster(dataframe_out(dataframe, dataframe.hpi_regional_column)),
            "hpi_global_df": forecaster(dataframe_out(dataframe, dataframe.hpi_global_column)),
            "prices_global_df": forecaster(dataframe_out(dataframe, dataframe.price_global_column)),
            "prices_regional_df": forecaster(dataframe_out(dataframe, dataframe.price_regional_column)),
            "region": dataframe.get_region()}
