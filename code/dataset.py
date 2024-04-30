import pandas as pd
import statsmodels.api as sm
import numpy as np

def create_output_df(data, code, smoothing_param=6.25):
    '''Create a dataframe with the Hodrick-Prescott detrended output gap for a specific country code.

    Args:
    data (DataFrame): The dataset containing GDP per capita information.
    code (str): The country code for which the output gap is calculated.
    smoothing_param (int, optional): The smoothing parameter for the Hodrick-Prescott filter. Default is 1600.

    Returns:
    DataFrame: DataFrame containing the output gap for the specified country code.

    This function filters the dataset to extract GDP per capita information for the specified country code.
    It then applies the Hodrick-Prescott filter to detrend the GDP per capita data, using the provided smoothing parameter.
    The output gap is calculated as the percentage deviation of GDP per capita from its trend.
    The function returns a DataFrame containing the output gap values.

    '''

    # Filter data for the specified country code
    df = data.loc[data['Code'] == code]

    # Apply Hodrick-Prescott filter to detrend GDP per capita
    cycle, trend = sm.tsa.filters.hpfilter(df.GDP_per_capita, lamb=smoothing_param)

    # Calculate output gap
    output_gap = round(((df.GDP_per_capita - trend) / trend) * 100, 2)

    # Create output DataFrame
    output_df = pd.DataFrame({
        'CC3': df.Code,
        'Year': df.Year,
        'output_gap': output_gap
    })

    return output_df

def merge_datasets(dataset1, dataset2, on=['Year', 'CC3'], how='left'):
    '''Merge two datasets based on specified columns.

    Args:
    dataset1 (DataFrame): The first dataset to merge.
    dataset2 (DataFrame): The second dataset to merge.
    on (list, optional): Columns to merge on. Defaults to ['Year', 'CC3'].
    how (str, optional): Type of merge to be performed. Defaults to 'left'.

    Returns:
    DataFrame: Merged DataFrame.
    '''
    merged_df = pd.merge(dataset1, dataset2, on=on, how=how)
    return merged_df

def concat_dataset(dataset1, dataset2, list, how, smoothing_param=6.25):
    '''Concatenate datasets for multiple countries.

    Args:
    dataset1 (DataFrame): The first dataset to concatenate.
    dataset2 (DataFrame): The second dataset to concatenate.
    country_list (list): List of country codes to include in the concatenated dataset.
    how (str, optional): Type of concatenation to be performed. Defaults to 'left'.
    smoothing_param (int, optional): The smoothing parameter for the Hodrick-Prescott filter. Default is 6.25.

    Returns:
    DataFrame: Concatenated DataFrame.
    '''
    all_datasets = []
    for code in list:
        # Merge datasets for each country code
        df = merge_datasets(dataset1[dataset1["CC3"]==code], create_output_df(dataset2, code, smoothing_param), how = how)
        all_datasets.append(df)

    # Concatenate all datasets
    concat_dataset = pd.concat(all_datasets,ignore_index=True)

    return concat_dataset

def dummy_variable(dataset):
    '''
    Creates dummy variables based on specific conditions in the dataset.

    Args:
    - dataset (DataFrame): The dataset containing various the informations for a list of countries.

    The function generates dummy variables for different conditions:
    1. 'banking_crisis_only': 1 if it's a year with a banking crisis but no inflation or currency crisis and has non-NaN inflation values, otherwise 0.
    2. 'excluded_years': 1 if it's a year with either an inflation crisis or a currency crisis, otherwise 0.
    3. 'banking_crisis_only_first_year': 1 if it's the first year of a banking crisis without an inflation or currency crisis in the previous year and has non-NaN inflation values, otherwise 0.
    4. 'recovery_only': 1 if it's a year without a banking, inflation, or currency crisis and has non-NaN inflation values, otherwise 0.
    '''

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
                                    (dataset['currency_crisis'] != 1) &
                                    not_nan_mask)
    dataset['recovery_only'] = dataset['recovery_only'].astype(int)

    return
