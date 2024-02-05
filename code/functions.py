import pandas as pd
import statsmodels.api as sm
import numpy as np


def create_output_df(data, code):
    df = data.loc[data['Code'] == code]
    cycle, trend = sm.tsa.filters.hpfilter(df.GDP_per_capita, lamb=1600)
    dataframe = pd.DataFrame({
    'CC3': df.Code,
    'Year' : df.Year,
    'output_gap' : round(((df.GDP_per_capita - trend)/trend)*100, 2)})
    return dataframe

def merge_datasets(dataset1, dataset2, on=['Year', 'CC3'], how='left'):
    merged_df = pd.merge(dataset1, dataset2, on=on, how=how)
    return merged_df

def concat_dataset(dataset1, dataset2, list):
    all_datasets = []
    for code in list:
        df = merge_datasets(create_output_df(dataset2[dataset2["CC3"]==code], dataset1, code))
        all_datasets.append(df)

    concat_dataset = pd.concat(all_datasets,ignore_index=True)
    return concat_dataset

def extract_inflation_series(data, target_year):
    target_index = data[data['Year'] == target_year].index[0]
    series = data.loc[target_index-1:target_index+6, 'annual_inflation']
    return np.array(series)

def extract_output_gap_series(data, target_year):
    target_index = data[data['Year'] == target_year].index[0]
    series = data.loc[target_index-1:target_index+6, 'output_gap']
    return np.array(series)

def years_xaxis(length):
    years = []
    for i in range (-1,length):
        if i<0:
            years.append(f"t{i}")
        elif i==0:
            years.append(f"t")
        else:
            years.append(f"t+{i}")
    return years
