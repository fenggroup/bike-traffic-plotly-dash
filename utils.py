# a collection of utility functions

import pandas as pd
import config

# A function to prossess the raw data from bike counter to a pandas dataframe
def df_process(data_file_name, date_range):

    path = './data/' + data_file_name

    df = pd.read_excel(path, names=['time', 'in', 'out'], skiprows=3)

    df['bi_direction'] = df['in'] + df['out']

    df['time'] = pd.to_datetime(df['time'])

    df = df.set_index('time')

    df = df[date_range[0]: date_range[1]]

    return df


# A function to get the daily weather data
def weather_data(weather_file_name):

    path = './data/' + weather_file_name

    df_temp = pd.read_csv(path, usecols=['DATE', 'PRCP', 'TMAX', 'TMIN'])

    # Convert the time to a pandas datetime object
    df_temp['DATE'] = pd.to_datetime(df_temp['DATE'])

    df_temp = df_temp.set_index('DATE')

    return df_temp

def note_data(note_file_name):

    path = './data/' + note_file_name

    df_temp = pd.read_csv(path)

    # Convert the time to a pandas datetime object
    df_temp['date'] = pd.to_datetime(df_temp['date'])

    df_temp = df_temp.set_index('date')

    return df_temp


# A function to update the dataframe based on the specified resample rule and date range
def df_update(df, rule, start_date, end_date):

    df_resample = df.resample(rule).sum()

    df_filtered = df_resample[(df_resample.index.strftime("%Y-%m-%d") >= start_date) & 
                              (df_resample.index.strftime("%Y-%m-%d") <= end_date)]

    df_filtered["day_of_week"] = df_filtered.index.strftime("%a")

    return df_filtered


# A function to convert rgb to rgba with transparency (alpha) value
def rgb2rgba(rgb, alpha):
    return 'rgba' + rgb[3:-1]  + ', ' + str(alpha) + ')'

