import pandas as pd

def preprocess_global_crises_data(dataset):
    '''
    Preprocess the global crises dataset.

    Args:
    dataset (DataFrame): The dataset containing global crises data.

    Returns:
    None: Modifies the dataset in place.
    '''

    # Drop the first header row
    dataset.drop(0, inplace = True)

    # Rename columns for consistency and clarity
    dataset.rename(columns={'Banking Crisis ':'banking_crisis',
                    'Systemic Crisis':'systemic_crisis',
                    'Banking_Crisis_Notes':'notes',
                    'Currency Crises':'currency_crisis',
                    'Inflation Crises':'inflation_crisis',
                    'Gold Standard':'gold_standard',
                    'SOVEREIGN EXTERNAL DEBT 1: DEFAULT and RESTRUCTURINGS, 1800-2012--Does not include defaults on WWI debt to United States and United Kingdom and post-1975 defaults on Official External Creditors': 'sovereign_external_debt_1',
                    'SOVEREIGN EXTERNAL DEBT 2: DEFAULT and RESTRUCTURINGS, 1800-2012--Does not include defaults on WWI debt to United States and United Kingdom but includes post-1975 defaults on Official External Creditors': 'sovereign_external_debt_2',
                    'Inflation, Annual percentages of average consumer prices':'annual_inflation'},
            inplace = True)

    # Convert 'Year' column to integer type
    dataset['Year'] = dataset['Year'].astype(int)

    # Convert certain columns to numeric type
    columns_to_convert = ['banking_crisis', 'systemic_crisis', 'annual_inflation', 'currency_crisis', 'inflation_crisis']
    dataset[columns_to_convert] = dataset[columns_to_convert].apply(pd.to_numeric, errors='coerce')

def preprocess_mdp_data(dataset):
    '''
    Preprocess the mdp dataset.

    Args:
    dataset (DataFrame): The dataset containing mdp data.

    Returns:
    None: Modifies the dataset in place.
    '''
    # Drop the '417485-annotations' column
    dataset.drop(columns='417485-annotations', inplace = True)

    # Rename the 'GDP per capita' column for consistency
    dataset.rename(columns={'GDP per capita':'GDP_per_capita'}, inplace = True)
