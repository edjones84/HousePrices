from neuralprophet import NeuralProphet
from neuralprophet import df_utils
from src.api import HousePriceIndexAPI
import pandas as pd
import os

if __name__ == '__main__':
    # N.B due to limits with the land registry api this will hit a error if it is run a lot
    dataframe = pd.read_csv("resources/example.csv").rename(columns={"month": "ds", "average_price_regional": "y"})
    df = dataframe[["ds", "y"]]
    df['ds'] = pd.to_datetime(df['ds'])

    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    m = NeuralProphet()
    df_fit = m.fit(df,"M")
    df_future = m.make_future_dataframe(df)
    forecast = m.predict(df=df_future)
    print(forecast)
