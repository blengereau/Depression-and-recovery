import pandas as pd

# Getting the crisis duration
def compute_crisis_duration(dataset):
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
        # Extract the serie only if the value of the inflation rate is not a NaN value
            if row['banking_crisis_only_first_year'] == 1:
                # Extract data during a crisis
                if index - 1 >= 0:
                    current_serie.append(data.at[index - 1, 'annual_inflation'])
                current_serie.append(row['annual_inflation'])
                for i in range(1,9):
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
            for i in range(1,10):
                if data.at[index + i, 'inflation_crisis'] == 1  or pd.isna(data.at[index + i,'output_gap']) or data.at[index + i, 'currency_crisis'] == 1 or (data.at[index + i, 'banking_crisis_only_first_year'] == 1):
                    break
                current_serie.append(data.at[index + i,'output_gap'])
            series.append(current_serie)
            current_serie = []
    return series

# Functions for crisis and recovery dynamics
def inflation_dynamics(data, during_crisis=True):

    ''' This function is extracting the series of the annual inflation rate for each banking crisis or recovery period.
    Input:
    - dataframe
    - during_crisis = True or False (True for the series each banking crisis, False for the series of each recovery period)
    Output:
    - a list of series

    If during_crisis = True:
        The function extracts the series of the inflation rate for time [Ts-1,..., Te]
        s being the year of the beginning ot the crisis, e being the last year of the crisis.
    If during_crisis = False:
        The function extracts the series of the inflation rate for time [Te+1,..., Ts-1]
        e being the last year of the previous crisis, s being the year of the beginning ot the next crisis.
    '''

    series = []
    crisis_started = False
    recovery_started = False
    first_year_appended = False
    excluded_year_during_crisis = False
    current_serie = []

    for index, row in data.iterrows():
        # Extract the serie only if the value of the value of the inflation rate is not a NaN value
        if not pd.isna(row['annual_inflation']):
            if during_crisis:
                # Extract data during a crisis
                if row['banking_crisis'] == 1:
                    if not crisis_started:
                        crisis_started = True
                        if row['banking_crisis_only_first_year'] == 1:
                            # Append the inflation rate for the year before the crisis
                            if index - 1 >= 0:
                                current_serie.append(data.at[index - 1, 'annual_inflation'])
                            current_serie.append(row['annual_inflation'])
                            first_year_appended = True
                    else:
                        if row['banking_crisis_only'] == 1 and first_year_appended and not excluded_year_during_crisis:
                            # Continue the existing series
                            current_serie.append(row['annual_inflation'])
                        else:
                            excluded_year_during_crisis = True

                elif crisis_started:
                    # End the series when a 0 is recorded in the banking_crisis column
                    crisis_started = False
                    if len(current_serie)>0:
                        series.append(current_serie)
                    current_serie = []
                    first_year_appended = False
                    excluded_year_during_crisis = False
            else:
                # Extract data during a non-crisis period
                if row['recovery_only'] == 1:
                    recovery_started = True
                    current_serie.append(row['annual_inflation'])
                elif recovery_started:
                    # End the series when a 0 is recorded in the banking_crisis column
                    recovery_started = False
                    # current_serie = np.array(current_serie)
                    series.append(current_serie)
                    # current_serie = current_serie.tolist()
                    current_serie = []
    return series

def output_gap_dynamics(data, during_crisis=True):

    series = []
    crisis_started = False
    no_crisis_period = False
    first_year_appended = False
    excluded_year_during_crisis = False
    current_serie = []

    for index, row in data.iterrows():
        # Extract the serie only if the value of the value of the inflation rate is not a NaN value
        if during_crisis:
            # Extract data during a crisis
            if row['banking_crisis_only'] == 1:
                if not crisis_started:
                    crisis_started = True
                    if row['banking_crisis_only_first_year'] == 1:
                    # Append the inflation rate for the year before the crisis
                        if index - 1 >= 0:
                            current_serie.append(data.at[index - 1, 'output_gap'])
                        current_serie.append(row['output_gap'])
                        first_year_appended = True
                else:
                    if row['banking_crisis_only'] == 1 and first_year_appended and not excluded_year_during_crisis:
                        # Continue the existing series
                        current_serie.append(row['output_gap'])
                    else:
                        excluded_year_during_crisis = True
            elif crisis_started:
                # End the series when a 0 is recorded in the banking_crisis column
                crisis_started = False
                if len(current_serie)>0:
                    series.append(current_serie)
                current_serie = []
                first_year_appended = False
                excluded_year_during_crisis = False
        else:
            # Extract data during a non-crisis period
            if row['recovery_only'] == 1:
                if not no_crisis_period:
                    no_crisis_period = True
                    # Append the inflation rate for the current year
                    current_serie.append(row['output_gap'])
                else:
                    # Continue the existing series
                    current_serie.append(row['output_gap'])
            elif no_crisis_period:
                # End the series when a 0 is recorded in the banking_crisis column
                no_crisis_period = False
                # current_serie = np.array(current_serie)
                series.append(current_serie)
                # current_serie = current_serie.tolist()
                current_serie = []
    # if not during_crisis:
    #     series = series[1:]
    return series
