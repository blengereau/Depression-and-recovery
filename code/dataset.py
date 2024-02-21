import pandas as pd
import statsmodels.api as sm
import numpy as np


#Dataset creation

def create_output_df(data, code):
    ''''From the dataset GDP_per_capita, this function create a dataframe the Hodrixk-Prescott detrended output gap for a specific country code.
    '''
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

def concat_dataset(dataset1, dataset2, list, how):
    all_datasets = []
    for code in list:
        df = merge_datasets(dataset2[dataset2["CC3"]==code], create_output_df(dataset1, code), how = how)
        all_datasets.append(df)

    concat_dataset = pd.concat(all_datasets,ignore_index=True)
    return concat_dataset


# Create dummy variable

def dummy_variable(dataset):

    # Generate a boolean mask where True indicates non-NaN values
    not_nan_mask = ~np.isnan(dataset['annual_inflation'])

    # Creating a dummy for the years with a banking crisis and no inflation crisis
    dataset['banking_crisis_only'] = ((dataset['banking_crisis'] == 1) &
                                        (dataset['inflation_crisis'] != 1) &
                                        (dataset['currency_crisis'] != 1) &
                                        not_nan_mask )
    dataset['banking_crisis_only'] = dataset['banking_crisis_only'].astype(int)

    #Create a dummy variable for excluded years
    dataset['excluded_years'] = ((dataset['inflation_crisis'] == 1) | (dataset['currency_crisis'] == 1)).astype(int)

    # Creating a dummy for the first years of crisis
    dataset['banking_crisis_only_first_year'] = 0
    last_crisis_year = None
    previous_year_exlcuded = None
    previous_year_inflation_is_nan = None

    for index, row in dataset.iterrows():
        if row['banking_crisis'] == 1:
            if row['banking_crisis_only'] == 1 and previous_year_exlcuded != 1 and not previous_year_inflation_is_nan :
                if last_crisis_year is None:
                    dataset.at[index, 'banking_crisis_only_first_year'] = 1
                if ((last_crisis_year is not None and row['Year'] - last_crisis_year >= 2) or (last_crisis_year is not None and row['Year'] - last_crisis_year <0)):
                    dataset.at[index, 'banking_crisis_only_first_year'] = 1
            last_crisis_year = row['Year']
        previous_year_exlcuded = row['excluded_years']
        previous_year_inflation_is_nan = np.isnan(row['annual_inflation'])

    #Create a dummy for recovery period
    dataset['recovery_only'] = ((dataset['banking_crisis'] != 1) &
                                    (dataset['inflation_crisis'] != 1) &
                                    (dataset['systemic_crisis'] != 1) &
                                    (dataset['currency_crisis'] != 1) &
                                    not_nan_mask)
    dataset['recovery_only'] = dataset['recovery_only'].astype(int)

    return
