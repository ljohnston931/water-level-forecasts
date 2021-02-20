"""
Feb 19, 2021
Created by Tanner Harrison

The purpose of this script is to take weather data stored in several .dly files and lake depth data stored in a .csv file and combine the two into a merged .csv file.
"""

import pandas as pd
import numpy as np
import sys


START_YEAR = 2019
DAYS_PER_MONTH = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
FORMAT = '%Y-%m-%d'

def format_yyyy_mm_dd(year, month, day):
    return str(year) + "-" + str(month).rjust(2, "0") + "-" + str(day).rjust(2, "0")

def parse_weather_data(weather_data_filename):
    df = pd.read_csv(weather_data_filename)
    columns = df.columns
    
    #We do the naive thing and ignore all of the flags
    drop_columns = ["ID"] +\
        [col for col in columns if col.startswith("MFLAG")] +\
        [col for col in columns if col.startswith("SFLAG")] +\
        [col for col in columns if col.startswith("QFLAG")]
    df = df.drop(columns = drop_columns)
    
    #We only worry about keeping PRCP, SNOW, SNWD, TMIN, and TMAX
    keep_elements = ["PRCP", "SNOW", "SNWD", "TMIN", "TMAX"]
    df = df[df.ELEMENT.isin(keep_elements)]
    
    df = df.replace(-9999, np.nan)
    
    indices = set()
    
    new_df = pd.DataFrame(columns = keep_elements)
        
    #we have to change things from one row per month to one row per day
    for i in df.index:
        if i % 100 == 0:
            print(f"{i} rows out of {max(df.index)} rows completed")
        year = df.loc[i].YEAR
        month = df.loc[i].MONTH
        element = df.loc[i].ELEMENT
        
        for day in range(1, DAYS_PER_MONTH[month] + 1):
            date_str = format_yyyy_mm_dd(year, month, day)
            date = pd.to_datetime(date_str, format=FORMAT)
            value = df.loc[i]["VALUE" + str(day)]
            if value != np.nan and date not in indices:
                new_df.loc[date] = [np.nan for label in keep_elements]
                indices.add(date)
            new_df.loc[date][element] = value
            
    return new_df

def parse_lake_data(lake_data_csv):
    """
    Returns a pandas dataframe with a date column and lake depth column
    """

    with open(lake_data_csv) as ifile:
        # Code from "lucy_cleans_historical_sl_data.ipynb"
        df = pd.read_table("raw_salt_lake_historical_data.txt", index_col=2, parse_dates=True)
        df = df.iloc[1:]
        df = df.drop(columns=['agency_cd', 'site_no', '178323_62614_00003_cd'])
        df.columns = ['depth']
        df.index = pd.to_datetime(df.index)
        df.depth = pd.to_numeric(df.depth)

        return df

def combine_lake_and_weather_data(lake_df, weather_df):
    both_df = weather_df.merge(lake_df, how = "outer", left_index = True, right_index = True)
    return both_df








def main(lake_csv, weather_csv, output_filename = "dataset.csv"):
    """
    This function takes the names for the lake depth and weather data files and creates a combined .csv file

    @param csv_filename (str): the name of the lake depth data file
    @param dly_filename (str): a list of the names of the weather data filenames

    @return (None)
    """
    lake_df = parse_lake_data(lake_csv)
    weather_df = parse_weather_data(weather_csv)

    both_df = combine_lake_and_weather_data(lake_df, weather_df)

    both_df.to_csv(output_filename)


"""
USAGE: lake_data.csv weather_data.csv output_file.csv
"""
if __name__ == "__main__":
    _, lake_csv, weather_csv, output_filename = sys.argv
    main(lake_csv, weather_csv, output_filename)