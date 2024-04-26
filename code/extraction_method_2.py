import pandas as pd

def compute_crisis_duration(dataset):
    '''
    Compute the duration of crisis events in the dataset.

    Args:
    dataset (DataFrame): The dataset containing crisis event information.

    Returns:
    list: A list containing the duration of each crisis event.
    '''
    crisis_duration = []  # List to store the duration of each crisis event
    current_length = 0  # Variable to track the length of the current crisis event sequence
    last_index = 0  # Variable to store the index of the last row processed

    for index, row in dataset.iterrows():
        if current_length > 0:
            # Continue the current crisis event sequence if it's ongoing
            if row['banking_crisis'] == 1 and row['banking_crisis_only_first_year'] != 1 and row['excluded_years'] != 1 and not pd.isna(row['annual_inflation']):
                # Increment the length of the current crisis event sequence
                if index == last_index + current_length: # Check that the crisis years are following themselces when we are adding a year to the length of the crisis
                    current_length += 1

            elif row['excluded_years']==1:
                # If an excluded year (inflation/currency crisis) is within the period between the first year of a crisis and 9 years after, reset the current_length to 0
                if index < (last_index + 9):
                    current_length = 0

            elif row['banking_crisis_only_first_year'] == 1:
                # If another banking crisis begin, append the length of the previous one to the crisis_duration list and start to count the length of the new crisis
                crisis_duration.append(current_length)
                current_length = 1
                # Track the index of the first year of the crisis currently counted
                last_index = index

        elif row['banking_crisis_only_first_year'] == 1:
            # Start a new crisis event sequence with a length of 1
            current_length += 1
            last_index = index

    # Check if the last sequence extends to the end of the dataset and append its duration to the crisis_duration list
    if current_length > 0:
        crisis_duration.append(current_length)

    return crisis_duration

def length_frequency(crisis_duration):
    '''
    Compute the frequency of different crisis durations.

    Args:
    crisis_duration (list): A list containing the duration of each crisis event.

    Returns:
    DataFrame: A DataFrame containing the frequency of each crisis duration.

    '''
    length_counts = {}
    for length in crisis_duration:
        length_counts[length] = length_counts.get(length, 0) + 1

    # Convert dictionary to pandas DataFrame
    frequency_table = pd.DataFrame(list(length_counts.items()), columns=['Length in years','Count'])
    frequency_table = frequency_table.sort_values(by='Length in years').reset_index(drop=True)

    # # # Add a number of data points column
    # len_freq['Number of points'] = len_freq['Count'].sum() - len_freq['Count'].cumsum() + len_freq['Count']

    return frequency_table

def extract_inflation_series(data):
    '''
    Extract series of inflation rates during the first year of each crisis until another crisis occurs.

    Args:
    data: DataFrame from which we use the following columns:
        - 'annual_inflation': Inflation rate for each year.
        - 'banking_crisis_only_first_year': Indicates if it's the first year of a banking crisis (1 if yes, 0 if no).
        - 'inflation_crisis': Indicates if it's an inflation crisis year (1 if yes, 0 if no).
        - 'currency_crisis': Indicates if it's a currency crisis year (1 if yes, 0 if no).

    Returns:
    - list: A list of lists, where each inner list represents a series of inflation rates during the first year of a crisis.
    '''
    series = []
    current_serie = []

    for index, row in data.iterrows():
        if not pd.isna(row['annual_inflation']):
        # Extract the serie only if the value of the inflation rate is not a NaN value
            if row['banking_crisis_only_first_year'] == 1:
                # Start of a potential series during a banking crisis

                # Append the inflation rate of the previous year if it exists
                if index - 1 >= 0:
                    current_serie.append(data.at[index - 1, 'annual_inflation'])

                # Append the inflation rate of the current year
                current_serie.append(row['annual_inflation'])

                # Iterate through the next 8 years to check for continuation of the series
                for i in range(1,9):
                    if (index + i) >= len(data):
                        # Reached the end of the dataset, so stop
                        break

                    elif data.at[index + i, 'banking_crisis_only_first_year'] == 1:
                        # Another banking crisis occurred, so stop the current series
                        break

                    elif data.at[index + i, 'inflation_crisis'] == 1  or pd.isna(data.at[index + i,'annual_inflation']) or data.at[index + i, 'currency_crisis'] == 1:
                        # An inflation crisis, NaN value, currency crisis, or another banking crisis occurred, so stop the current series
                        current_serie = [] # Reset the current serie
                        break

                    # Append the inflation rate of the next year if we passed the two previous conditions and the loop isn't broken
                    current_serie.append(data.at[index + i,'annual_inflation'])

                # If the current series is not empty, append it to the list of series
                if len(current_serie)>0:
                    series.append(current_serie)

                # Reset the current series for the next iteration
                current_serie = []

    return series

def normalize_serie(list):
    '''
    Normalize each sublist in the given list based on its first element.

    Args:
    list (list): A list of lists, where each sublist represents a series of crisis data.

    Returns:
    list: A list of lists, where each sublist is normalized based on its first element.
    '''
    # Create an empty list to store the normalized series
    normalized_list = []

    # Iterating through each sublist of the list
    for sublist in list:
        # Substracting to each value of the sublist the value of the first element of the sublist
        first_element = sublist[0]
        normalized_sublist = [round(value - first_element,2) for value in sublist]
        # Append the normalized to its first value sublist to list contaning the normalized series
        normalized_list.append(normalized_sublist)
    return normalized_list


def extract_output_gap_series(data):
    '''
    Extract series of output gaps for each first year of banking crisis until another crisis occurs or NaN values are encountered.

    Args:
    data (DataFrame): The dataset containing crisis event information.

    Returns:
    list: A list of lists, where each sublist represents a series of output gaps for a banking crisis event.
    '''

    series = []
    current_serie = []

    # Iterate through each row in the DataFrame
    for index, row in data.iterrows():
        if row['banking_crisis_only_first_year'] == 1:
            # Start a new series if it's the first year of a banking crisis. Don't start a series if the crisis occurs at the first row of the dataset as no information for ts-1 would be available

            if index - 1 >= 0:
                # Append output gap for ts-1 if it exists
                current_serie.append(data.at[index - 1, 'output_gap'])
            # Append output gap for the current year
            current_serie.append(row['output_gap'])

            # Append output gaps for the next 8 years until another crisis or NaN value in the output gap is encountered
            for i in range(1,9):
                if (index + i) >= len(data):
                    # Reached the end of the dataset, so stop
                    break

                if data.at[index + i, 'banking_crisis_only_first_year'] == 1:
                    # Another banking crisis occurred, so stop the current series
                    break

                elif data.at[index + i, 'inflation_crisis'] == 1  or pd.isna(data.at[index + i,'annual_inflation']) or data.at[index + i, 'currency_crisis'] == 1:
                    # An inflation crisis, NaN value or currency crisis has occured so stop the current series and reset it
                    current_serie = []
                    break
                # Append the output gap of the next year
                elif (row['Year'] + i) == (data.at[index + i,'Year']): # Checking that the years follow each other as in the output gap dataset some data can be missing
                    current_serie.append(data.at[index + i,'output_gap'])

            # If the current series is not empty, it means that we didn't dropped it because it contained an inflation / currency crisis so we can append it.
            if len(current_serie)>0:
                series.append(current_serie)
            current_serie = []
    return series

def inflation_dynamics(data, during_crisis=True):
    '''
    Extracts series of annual inflation rates for each banking crisis or recovery period.

    Args:
    - data (DataFrame): The dataset containing crisis event information.
    - during_crisis (bool): True to extract series for each banking crisis, False for recovery periods.

    Returns:
    - list: A list of series, where each sublist represents a series of annual inflation rates.

    If during_crisis is True:
        The function extracts the series of inflation rates for each banking crisis.
        Each series spans from the year before the crisis starts (ts-1) to the year before the crisis ends (te-1)
        but stops if another banking crisis begins. If an exluded year occurs, the serie is dropped.
    If during_crisis is False:
        The function extracts the series of inflation rates for each recovery period.
        Each series spans from the year after the crisis ends to the year before the next crisis starts
        but stops if an exluded year occurs.
    '''
    # List
    series = [] # List to store extracted series
    current_serie = []  # Current series being constructed

    # Flags
    crisis_started = False # Flag indicating if a crisis period has started
    recovery_started = False  # Flag indicating if a recovery period has started
    first_year_appended = False  # Flag indicating if the first year's data is appended to the current series
    excluded_year_during_crisis = False  # Flag indicating if a a crisis contains an excluded years
    excluded_year_during_recovery = False  # Flag indicating if a a recovery period cotains an excluded year
    crisis_occured = False  # Flag indicating if a crisis has occurred
    previous_year = 0  # Variable to track the previous year

    # Iterating through the dataset
    for index, row in data.iterrows():
        # Extract the serie only if the value of the value of the inflation rate is not a NaN value
        if not pd.isna(row['annual_inflation']):
            # Extract the inflation rate during a banking crisis
            if during_crisis:
                if row['banking_crisis'] == 1:
                    if not crisis_started:
                        crisis_started = True
                        if row['banking_crisis_only_first_year'] == 1 and (index - 1) >= 0:
                            # Append the inflation rate from ts-1 to ts
                            current_serie.append(data.at[index - 1, 'annual_inflation'])
                            current_serie.append(row['annual_inflation'])
                            first_year_appended = True
                    # If a crisis already begun, continue appending
                    else:
                        if (row['banking_crisis_only'] == 1 and
                            first_year_appended and  # Prevent to append years if the first year has not been appended
                            not excluded_year_during_crisis): # Prevent appending years if an excluded year occured during the crisis prior that year
                            # Continue the existing series
                            current_serie.append(row['annual_inflation'])
                        else:
                            # If the row has 1 in the banking_crisis column but 0 in the banking_crisis_only, it means that this row is an excluded year
                            excluded_year_during_crisis = True
                            current_serie = [] # Drop the serie if an excluded year occured. Reset current_serie to an empty list

                # End the series when a 0 is recorded in the banking_crisis column and a if a crisis has been recorded before
                elif crisis_started:
                    crisis_started = False

                    # Append the serie only if the current_serie is not empty
                    if len(current_serie)>0:
                        series.append(current_serie)
                    # Reset the current_serie to 0 after apending it and reset flags
                    current_serie = []
                    first_year_appended = False
                    excluded_year_during_crisis = False

            # Extract the inflation rate during a recovery period post-crisis
            else:
                # Reset the crisis_occured flag each time the iteration process goes to another country
                if row['banking_crisis_only_first_year'] == 1:
                    crisis_occured = True
                    excluded_year_during_crisis = False
                elif (row['Year'] - previous_year) < 0:
                    crisis_occured = False

                # Start and continue the recovery serie if we are in a post-crisis recovery period with no excluded year that happened during the period
                if row['recovery_only'] == 1:
                    if crisis_occured and not excluded_year_during_recovery and not excluded_year_during_crisis:
                        recovery_started = True #Set the recovery flag to True
                        current_serie.append(row['annual_inflation']) # Append the inflation rate

                # Set the excluded year during recovery flag to True is an excluded year occurs during a recovery period
                elif row['excluded_years'] == 1 and row['banking_crisis'] != 1:
                    excluded_year_during_recovery = True

                # Set the excluded year during crisis flag to True is an excluded year occurs during a crisis, which would mean that we drop the serie in the method 2
                elif row['excluded_years'] == 1 and row['banking_crisis'] == 1:
                    excluded_year_during_crisis = True

                # End the serie if we enter in the next banking crisis period
                elif recovery_started:
                    recovery_started = False # Reset the flag of the recovery
                    series.append(current_serie) # Append the serie that we just had
                    current_serie = [] # Reset the current_serie list to collect a new serie
                    # Reset the two flags checking for excluded years
                    excluded_year_during_recovery = False
                    excluded_year_during_crisis = False

                # When we reach a new banking crisis, we reset the excluded_year_during_recovery flag to be able to append the recovery serie when the crisis will end
                else:
                    excluded_year_during_recovery = False

            previous_year = row['Year'] #We track the year of each row after a new iteration in the dataset to see if we change of country

    if len(current_serie)>0: # Be sure to only append non-empty serie
        series.append(current_serie)
    return series

def output_gap_dynamics(data, during_crisis=True):
    '''
    Extracts series of output gap values for each banking crisis or recovery period.

    Args:
    - data (DataFrame): The dataset containing crisis event information.
    - during_crisis (bool): True to extract series for each banking crisis, False for recovery periods.

    Returns:
    - list: A list of series, where each sublist represents a series of output gap values.

    If during_crisis is True:
        it extracts series for each banking crisis, spanning from the year before the crisis starts (ts-1) to the year before the crisis ends (te-1).
        The serie is dropped if an inflation/currency crisis occurs during the previous banking crisis.
    If during_crisis is False:
        it extracts series for each recovery period, spanning from the year after the crisis ends to the year before the next crisis starts but stops if an excluded year occurs.
        We don't append the recovery serie if an inflation/currency crisis occured during the previous banking crisis.
    '''
    # List
    series = [] # List to store extracted series
    current_serie = []  # Current series being constructed

    # Flags
    crisis_started = False # Flag indicating if a crisis period has started
    recovery_started = False  # Flag indicating if a recovery period has started
    first_year_appended = False  # Flag indicating if the first year's data is appended to the current series
    excluded_year_during_crisis = False  # Flag indicating if a a crisis contains an excluded years
    excluded_year_during_recovery = False  # Flag indicating if a a recovery period cotains an excluded year
    crisis_occured = False  # Flag indicating if a crisis has occurred
    previous_year = 0  # Variable to track the previous year

    # Iterating through the dataset
    for index, row in data.iterrows():
        # Extract the serie only if the value of the value of the output gap is not a NaN value
        if not pd.isna(row['output_gap']):
            # Extract the output gap during a banking crisis
            if during_crisis:
                if row['banking_crisis'] == 1:
                    if not crisis_started:
                        crisis_started = True
                        if row['banking_crisis_only_first_year'] == 1 and (index - 1) >= 0:
                            # Append the output gap from ts-1 to ts
                            current_serie.append(data.at[index - 1, 'output_gap'])
                            current_serie.append(row['output_gap'])
                            first_year_appended = True
                    # If a crisis already begun, continue appending
                    else:
                        if (row['banking_crisis_only'] == 1 and
                            first_year_appended and  # Prevent to append years if the first year has not been appended
                            not excluded_year_during_crisis): # Prevent appending years if an excluded year occured during the crisis prior that year
                            # Continue the existing series
                            current_serie.append(row['output_gap'])
                        else:
                            # If the row has 1 in the banking_crisis column but 0 in the banking_crisis_only, it means that this row is an excluded year
                            excluded_year_during_crisis = True
                            current_serie = [] # Drop the serie if an excluded year occured. Reset current_serie to an empty list

                # End the series when a 0 is recorded in the banking_crisis column and a if a crisis has been recorded before
                elif crisis_started:
                    crisis_started = False

                    # Append the serie only if the current_serie is not empty
                    if len(current_serie)>0:
                        series.append(current_serie)
                    # Reset the current_serie to 0 after apending it and reset flags
                    current_serie = []
                    first_year_appended = False
                    excluded_year_during_crisis = False

            # Extract the output gap during a recovery period post-crisis
            else:
                # Reset the crisis_occured flag each time the iteration process goes to another country
                if row['banking_crisis_only_first_year'] == 1:
                    crisis_occured = True
                    excluded_year_during_crisis = False
                elif (row['Year'] - previous_year) < 0:
                    crisis_occured = False

                # Start and continue the recovery serie if we are in a post-crisis recovery period with no excluded year that happened during the period
                if row['recovery_only'] == 1:
                    if crisis_occured and not excluded_year_during_recovery and not excluded_year_during_crisis:
                        recovery_started = True #Set the recovery flag to True
                        current_serie.append(row['output_gap']) # Append the inflation rate

                # Set the excluded year during recovery flag to True is an excluded year occurs during a recovery period
                elif row['excluded_years'] == 1 and row['banking_crisis'] != 1:
                    excluded_year_during_recovery = True

                # Set the excluded year during crisis flag to True is an excluded year occurs during a crisis, which would mean that we drop the serie in the method 2
                elif row['excluded_years'] == 1 and row['banking_crisis'] == 1:
                    excluded_year_during_crisis = True

                # End the serie if we enter in the next banking crisis period
                elif recovery_started:
                    recovery_started = False # Reset the flag of the recovery
                    series.append(current_serie) # Append the serie that we just had
                    current_serie = [] # Reset the current_serie list to collect a new serie
                    # Reset the two flags checking for excluded years
                    excluded_year_during_recovery = False
                    excluded_year_during_crisis = False

                # When we reach a new banking crisis, we reset the excluded_year flags to be able to append the recovery serie when the crisis will end
                else:
                    excluded_year_during_recovery = False

            previous_year = row['Year'] #We track the year of each row after a new iteration in the dataset to see if we change of country

    if len(current_serie)>0: # Be sure to only append non-empty serie
        series.append(current_serie)
    return series
