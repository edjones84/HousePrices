import pandas as pd

from src.dataframe import InputDataFrame
from src.forecaster import apply

if __name__ == '__main__':
    # N.B due to limits with the land registry api this will hit a error if it is run a lot
    dataframe = pd.read_csv("resources/example.csv")
    in_df = InputDataFrame(dataframe=dataframe)
    out_dataframes = apply(in_df)
    print(out_dataframes)
