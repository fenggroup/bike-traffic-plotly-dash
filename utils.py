# a collection of utility functions
import numpy as np
import pandas as pd
import config

# A function to prossess the raw data from bike counter to a pandas dataframe
def df_process(data_file_name, date_range):

    path = './data/counter/' + data_file_name

    df = pd.read_excel(path, names=['time', 'in', 'out'], skiprows=3)

    df['bi_direction'] = df['in'] + df['out']

    df['time'] = pd.to_datetime(df['time'])

    df = df.set_index('time')

    df = df[date_range[0]: date_range[1]]

    df["2022-11-20":"2023-04-30"] = np.nan   # manually set the dates of no recording

    return df


# A function to get the daily weather data
def weather_data(weather_file_name):

    path = './data/weather/' + weather_file_name

    df_temp = pd.read_csv(path, usecols=['DATE', 'PRCP', 'TMAX', 'TMIN'])

    # Convert the time to a pandas datetime object
    df_temp['DATE'] = pd.to_datetime(df_temp['DATE'])

    df_temp = df_temp.set_index('DATE')

    return df_temp

def note_data(note_file_name):

    path = './data/notes/' + note_file_name

    df_temp = pd.read_csv(path)

    # Convert the time to a pandas datetime object
    df_temp['date'] = pd.to_datetime(df_temp['date'])

    df_temp = df_temp.set_index('date')

    return df_temp


# A function to update the dataframe based on the specified resample rule and date range
def df_update(df, rule, start_date, end_date, agg='sum'):

    if agg == 'sum':

        if rule == 'W':

            df_resample = df.resample(rule, label='left').agg(pd.Series.sum, min_count=1)  # make sure the resample result of NAN is not zero but NAN.
            df_resample.index = df_resample.index + pd.DateOffset(days=1)  # offset the index by a day
            # see the issue here: https://stackoverflow.com/questions/30989224/python-pandas-dataframe-resample-daily-data-to-week-by-mon-sun-weekly-definition/46712821#46712821

        else: 

            df_resample = df.resample(rule).agg(pd.Series.sum, min_count=1)  # make sure the resample result of NAN is not zero but NAN.

    elif agg == 'mean':

        if rule == 'W':

            df_resample = df.resample(rule, label='left').agg(pd.Series.mean)  # make sure the resample result of NAN is not zero but NAN.
            df_resample.index = df_resample.index + pd.DateOffset(days=1)  # offset the index by a day
            # see the issue here: https://stackoverflow.com/questions/30989224/python-pandas-dataframe-resample-daily-data-to-week-by-mon-sun-weekly-definition/46712821#46712821

        else: 

            df_resample = df.resample(rule).agg(pd.Series.mean)  # make sure the resample result of NAN is not zero but NAN.

    df_filtered = df_resample[(df_resample.index.strftime("%Y-%m-%d") >= start_date) & 
                              (df_resample.index.strftime("%Y-%m-%d") <= end_date)]

    df_filtered["day_of_week"] = df_filtered.index.strftime("%a")

    return df_filtered


# A function to convert rgb to rgba with transparency (alpha) value
def rgb2rgba(rgb, alpha):
    return 'rgba' + rgb[3:-1]  + ', ' + str(alpha) + ')'

