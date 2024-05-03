import os
import sys
import pandas as pd
import glob


def process_temperature(df):
    temp_str = df.str.split(',').str[0]
    celsius_scaled = temp_str.astype(float)
    celsius = celsius_scaled / 10.0
    fahrenheit = celsius * 1.8 + 32

    return fahrenheit


def process_windspeed(df):
    windspeed_str = df.str.split(',').str[3]
    windspeed_scaled = windspeed_str.astype(float)
    wind_speed = windspeed_scaled / 10.0

    return wind_speed


folder = sys.argv[1]

folder_dir = f"Data/Weather/{folder}"
files = glob.glob(f"{folder_dir}/*.csv")

output_dir = "Data/Weather"

dfs = []

for file in files:
    # Read CSV. These are how NA values are formatted in the datasets.
    df = pd.read_csv(file, usecols=['DATE', 'WND', 'TMP', 'DEW'] ,na_values=['+9999,9', '999,9,9,9999,9'])

    # Format for data is in #### format and scaled by 10 - e.g., 0034 is 3.4. Convert to regular format, and for temperature, convert to Fahrenheit.
    df['TMP'] = process_temperature(df['TMP'])
    df['DEW'] = process_temperature(df['DEW'])
    df['WND'] = process_windspeed(df['WND'])

    # Average the intrahour readings, so that there is only a single value to represent each hour.
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.index = df['DATE']
    df = df.resample('H').mean()

    # Interpolate missing values in the dataset. Will work well considering this is a time series dataset.
    df = df.interpolate(method='linear')

    # Round out values, as only whole numbers should be used in the model.
    df = df.round()

    # Reorder to make sure TMP is the first column after date.
    df = df[['TMP', 'DEW', 'WND']]

    # Calculate Temp in Celsius
    df['TMPc'] = (df['TMP'] - 32) * (5 / 9)

    # Calculate Temperature Cooling Requirement, Heating Requirement, and Extra Heating Requirements
    df['CR'] = df['TMPc'] - 20
    df.loc[df['CR'] < 0, 'CR'] = 0

    df['HR'] = 16.5 - df['TMPc']
    df.loc[df['HR'] < 0, 'HR'] = 0

    df['XHR'] = 5 - df['TMPc']
    df.loc[df['XHR'] < 0, 'XHR'] = 0

    # Drop TMPc column because we don't need
    df.drop(columns=['TMPc'], inplace=True)

    dfs.append(df)

df = pd.concat(dfs)
df.sort_values('DATE', inplace=True)

df.to_csv(f'Data/Weather/{folder}.csv')
