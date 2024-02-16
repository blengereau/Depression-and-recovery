import pandas as pd
import statsmodels.api as sm
import numpy as np

# Getting the crisis duration
def crisis_duration(dataset):
    crisis_duration = []
    current_length = 0

    for index, row in dataset.iterrows():
        if current_length > 0:
            if row['banking_crisis'] == 1:
                current_length += 1
            else:
                crisis_duration.append(current_length)
                current_length = 0
        else:
            if row['banking_crisis_only_first_year'] == 1:
                current_length = +1

    #Check if the last sequence extends to the end of the dataset
    if current_length > 0:
        crisis_duration.append(current_length)

    return crisis_duration

# Compute the frequency of each crisis length
def length_frequency(crisis_duration):
    length_counts = {}
    for length in crisis_duration:
        if length in length_counts:
            length_counts[length] += 1
        else:
            length_counts[length] = 1

    # Convert dictionary to pandas DataFrame
    len_freq = pd.DataFrame(list(length_counts.items()), columns=['Length','Count'])
    len_freq = len_freq.sort_values(by='Length')


    # # Add a number of data points column
    len_freq['Number of points'] = len_freq['Count'].sum() - len_freq['Count'].cumsum() + len_freq['Count']

    # Sort DataFrame by length
    len_freq.reset_index(drop=True, inplace=True)

    return len_freq

#Time series extraction
def extract_inflation_series(data):
    ''' We want here to return the series of the inflaion rate for each first year of crisis until an inflation crisis happen or another banking crisis occurs.'''
    series = []
    current_serie = []

    for index, row in data.iterrows():
        if not pd.isna(row['annual_inflation']):
        # Extract the serie only if the value of the value of the inflation rate is not a NaN value
            if row['banking_crisis_only_first_year'] == 1:
                # Extract data during a crisis
                if index - 1 >= 0:
                    current_serie.append(data.at[index - 1, 'annual_inflation'])
                current_serie.append(row['annual_inflation'])
                for i in range(1,7):
                    if data.at[index + i, 'inflation_crisis'] == 1  or pd.isna(data.at[index + i,'annual_inflation']) or data.at[index + i, 'currency_crisis'] == 1 or (data.at[index + i, 'banking_crisis_only_first_year'] == 1):
                        break
                    current_serie.append(data.at[index + i,'annual_inflation'])
                series.append(current_serie)
                current_serie = []
    return series

# Normalize inflation rate
def normalize_crisis_data(list):
    normalized_list = []
    for sublist in list:
        first_element = sublist[0]
        normalized_sublist = [round(value - first_element,2) for value in sublist]
        normalized_list.append(normalized_sublist)
    return normalized_list


def extract_output_gap_series(data):
    ''' We want here to return the series of the inflaion rate for each first year of crisis until an inflation crisis happen or another banking crisis occurs.'''
    series = []
    current_serie = []

    for index, row in data.iterrows():
        if row['banking_crisis_only_first_year'] == 1:
            # Extract data during a crisis
            if index - 1 >= 0:
                current_serie.append(data.at[index - 1, 'output_gap'])
            current_serie.append(row['output_gap'])
            for i in range(1,7):
                if data.at[index + i, 'inflation_crisis'] == 1  or pd.isna(data.at[index + i,'output_gap']) or data.at[index + i, 'currency_crisis'] == 1 or (data.at[index + i, 'banking_crisis_only_first_year'] == 1):
                    break
                current_serie.append(data.at[index + i,'output_gap'])
            series.append(current_serie)
            current_serie = []
    return series
