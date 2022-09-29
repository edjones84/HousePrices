from datetime import date

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
from postcodes_uk import Postcode

from src.multithread import MultiThreadAPI


class HousePriceIndexAPI:
    """This takes the house price index api to get average sold prices and the HPI from
    "https://www.landregistry.data.gov.uk/data/ukhpi/region """

    def __init__(self, postcode: str):
        self.postcode = postcode.upper()
        # get region from postcode
        self.region, self.district = postcode_to_region(self.postcode)
        self.country = requests.get(f"http://api.postcodes.io/postcodes/{postcode}").json()["result"]["country"].lower()
        self.df = pd.DataFrame(columns=["region", "average_price", "HPI", "month"])

    def get_house_price_index_json(self, district_region_country='region'):
        """returns json with average price and HPI for each month of last 10 years"""

        # loop to do api call each month for 240 months so 20 years and only output every 1 months
        global url_tmp
        years = 20
        months = years * 12
        interval = 1

        # Create list of all urls to pass through
        url_list = []
        for i in range(2, months + 2, interval):
            year_month = (date.today() - relativedelta(months=i)).strftime("%Y-%m")
            if district_region_country == 'region':
                url_tmp = f"https://landregistry.data.gov.uk/data/ukhpi/region/{self.region}/month/{year_month}.json"
            elif district_region_country == 'district':
                url_tmp = f"https://landregistry.data.gov.uk/data/ukhpi/region/{self.district}/month/{year_month}.json"
            elif district_region_country == 'country':
                url_tmp = f"https://landregistry.data.gov.uk/data/ukhpi/region/{self.country}/month/{year_month}.json"

            url_list.append(url_tmp)

        # run the multithreading to get the json data
        call = MultiThreadAPI(url_list)
        all_json = call.run_api_threads()

        return all_json

    @staticmethod
    def __create_dataframe(initial_df, json_data, name):
        """private method to create a dataframe from the land registry data"""
        df = initial_df
        if "averagePrice" in json_data["result"]["primaryTopic"]:
            average_price = json_data["result"]["primaryTopic"]["averagePrice"]
            HPI = json_data["result"]["primaryTopic"]["housePriceIndex"]
            month = json_data["result"]["primaryTopic"]["refMonth"]
            df = initial_df.append({'average_price': average_price,
                                    'region': name,
                                    'HPI': HPI,
                                    'month': month},
                                   ignore_index=True)
            df['month'] = pd.to_datetime(df['month'], errors='coerce').dt.strftime('%Y-%m-%d')
        else:
            pass
        return df

    def get_house_price_index_dataframe(self) -> DataFrame:
        """convert the json response to an output dataframe to be used in fast api
        globally means it gets ran on the whole of England,Scotland or Wales"""
        # dataframe schema
        df = self.df
        json_district = self.get_house_price_index_json('district')
        boolCheck = False
        # loop through checking if we have granular district data and if not use regional data
        for json_district_data in json_district:
            if "averagePrice" in json_district_data["result"]["primaryTopic"]:
                df = self.__create_dataframe(initial_df=df, json_data=json_district_data,
                                             name=self.district)
        if df.empty:
            json_region = self.get_house_price_index_json('region')
            for json_region_data in json_region:
                df = self.__create_dataframe(initial_df=df, json_data=json_region_data,
                                             name=self.region)
        return df

    def get_global_house_price_index_dataframe(self) -> DataFrame:
        """convert the json response to an output dataframe to be used in fast api
        globally means it gets ran on the whole of England,Scotland or Wales"""
        # dataframe schema
        df = self.df
        json_country = self.get_house_price_index_json('country')
        # loop through checking if we have granular district data and if not use regional data
        for json_country_data in json_country:
            df = self.__create_dataframe(initial_df=df, json_data=json_country_data,
                                         name=self.country)
        return df

    def combine_dataframe(self) -> DataFrame:
        """combine global and regional dataframes"""
        combined_df = pd.merge(self.get_global_house_price_index_dataframe(),
                               self.get_house_price_index_dataframe(),
                               how="inner",
                               on=["month"])
        combined_df.columns = combined_df.columns.str.replace("x", "global")
        combined_df.columns = combined_df.columns.str.replace("y", "regional")
        return combined_df.drop(columns=['region_global']).rename(columns={"region_regional": "region"})


def postcode_to_region(in_postcode: str, spaces_become="-") -> tuple:
    """Turn a postcode into a region in the UK and return a tuple of region and district"""
    postcode = Postcode.from_string(in_postcode)
    area = postcode.area

    # Read in the referance data to go to regions
    df = pd.read_csv("resources/UK_Region_Codes.csv")
    df_region = df[df['Postcode_prefix'] == area]
    region = df_region['UK_region'].to_string(index=False)
    district = df_region['Postcode_district'].to_string(index=False).lower()

    # format so that spaces become desired format and make it all lower case
    region_format = region.replace(" ", spaces_become).lower()

    # Turn any greater london strings to london
    if region_format == "greater-london":
        region_format = "london"
    else:
        region_format = region_format

    return region_format, district
