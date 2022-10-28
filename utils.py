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


def weather_data(weather_file_name):

    pa = './data/' + weather_file_name

    df_temp = pd.read_csv(pa, usecols=['DATE', 'PRCP', 'TMAX', 'TMIN'])

    # Convert the time to a pandas datetime object
    df_temp['DATE'] = pd.to_datetime(df_temp['DATE'])

    df_temp = df_temp.set_index('DATE')

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


# A function to set mark color based on travel direction
def find_mark_color(dir_radio_val, alpha):

    if dir_radio_val == 'in':

        mark_color = rgb2rgba(config.color_in, alpha)
    
    elif dir_radio_val == 'out':

        mark_color = rgb2rgba(config.color_out, alpha)

    elif dir_radio_val == 'bi_direction':

        mark_color = rgb2rgba(config.color_both_direction, alpha)
    
    return mark_color
