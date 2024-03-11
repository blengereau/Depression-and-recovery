import pandas as pd

def compute_crisis_duration(dataset):
    '''
    Compute the duration of crisis events in the dataset.

    Args:
    dataset (DataFrame): The dataset containing crisis event information.

    Returns:
    list: A list containing the duration of each crisis event.
    '''
    # Create a variable to count the length of the crises event when iterating through the dataset
    current_length = 0
    # Create a list to store the durations of every crisis
    crisis_duration = []

    # Create a loop to iterate through each row of the dataset
    for index, row in dataset.iterrows():
        # Check if we are currently in a crisis event
        if current_length > 0:
            # If the crisis event continues in the current year, add another year to the current_length variable
            if row['banking_crisis'] == 1:
                current_length += 1
            # If the crisis event ends, append the duration to crisis_duration list and reset current_length
            else:
                crisis_duration.append(current_length)
                current_length = 0
        # If we are not currently in a crisis event (current_length is 0) and it's the first year of a crisis event, start counting
        else:
            if row['banking_crisis_only_first_year'] == 1:
                current_length = +1

    #Check if the last sequence extends to the end of the dataset
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
    # Count the occurrences of each crisis duration
    length_counts = {}
    for length in crisis_duration:
        length_counts[length] = length_counts.get(length, 0) + 1

    # Convert dictionary to pandas DataFrame
    frequency_table = pd.DataFrame(list(length_counts.items()), columns=['Length_of_crisis','Number_of_crisis_event'])
    frequency_table = frequency_table.sort_values(by='Length_of_crisis').reset_index(drop=True)

    ## Add a number of data points column
    # frequency_table['Number of points'] = frequency_table['Number_of_crisis_event'].sum() - frequency_table['Number_of_crisis_event'].cumsum() + frequency_table['Number_of_crisis_event']

    return frequency_table

#Time series extraction
def extract_inflation_series(data):
    '''
    Extract series of inflation rates for each first year of crisis until another crisis occurs or NaN values are encountered.
    ts represents the starting year of a banking crisis.

    Args:
    data (DataFrame): The dataset containing crisis event information.

    Returns:
    list: A list of lists, where each sublist represents a series of inflation rates for a crisis event.
    '''
    series = []
    current_serie = []

    for index, row in data.iterrows():
        # Check if the inflation rate is not NaN
        if not pd.isna(row['annual_inflation']):
            # Start a new series if it's the first year of a banking crisis. Don't start a serie if the crisis occurs at the fist row of the dataset as no information for ts-1 would be available
            if row['banking_crisis_only_first_year'] == 1 and (index - 1 >= 0):
                # Extract data at ts-1 and ts.
                current_serie.append(data.at[index - 1, 'annual_inflation'])
                current_serie.append(row['annual_inflation'])
                # Append inflation rate for the next 9 years until an inflation / currency / new banking crisis or NaN value in the inflation rate is encountered
                for i in range(1,9):
                    if (data.at[index + i, 'inflation_crisis'] == 1  or
                        data.at[index + i, 'currency_crisis'] == 1 or
                        data.at[index + i, 'banking_crisis_only_first_year'] == 1 or
                        pd.isna(data.at[index + i,'annual_inflation'])):
                        break
                    current_serie.append(data.at[index + i,'annual_inflation'])
                # Append the cururent serie to the series list
                series.append(current_serie)
                # Resert the current serie to an empty list
                current_serie = []
    return series

def extract_output_gap_series(data):
    '''
    Extract series of output gaps for each first year of crisis until another crisis occurs or NaN values are encountered.

    Args:
    data (DataFrame): The dataset containing crisis event information.

    Returns:
    list: A list of lists, where each sublist represents a series of output gaps for a crisis event.
    '''

    series = []
    current_serie = []

    for index, row in data.iterrows():
        # As the dataset of the output gap do not contains NaN values, we don't have to specify to check if the output-gap is not NaN
        # Start a new series if it's the first year of a banking crisis
        if row['banking_crisis_only_first_year'] == 1:
            # Extract data during a crisis
            if index - 1 >= 0:
                current_serie.append(data.at[index - 1, 'output_gap'])
            current_serie.append(row['output_gap'])
            # Append the output-gap for the next 9 years until an inflation / currency / new banking crisis is encountered
            for i in range(1,9):
                if (data.at[index + i, 'inflation_crisis'] == 1  or
                    data.at[index + i, 'currency_crisis'] == 1 or
                    (data.at[index + i, 'banking_crisis_only_first_year'] == 1)):
                    break
                current_serie.append(data.at[index + i,'output_gap'])
            # Append the current serie to the series list
            series.append(current_serie)
            # Reser the cuurent serie to an empty list
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


# # Functions for crisis and recovery dynamics
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
        but stops if an exluded year occurs.
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
                elif (row['Year'] - previous_year) < 0:
                    crisis_occured = False

                # Start and continue the recovery serie if we are in a post-crisis recovery period with no excluded year that happened during the period
                if row['recovery_only'] == 1:
                    if crisis_occured and not excluded_year_during_recovery:
                        recovery_started = True #Set the recovery flag to True
                        current_serie.append(row['annual_inflation']) # Append the inflation rate
                # Set the excluded year during recovery flag to True is an excluded year occurs during a recovery period
                elif row['excluded_years'] == 1 and row['banking_crisis'] != 1:
                    excluded_year_during_recovery = True
                # End the serie if it not possible to continue appending the inflation rate
                elif recovery_started:
                    recovery_started = False
                    series.append(current_serie)
                    current_serie = []
                    excluded_year_during_recovery = False
                else:
                    excluded_year_during_recovery = False
            previous_year = row['Year']
    if len(current_serie)>0:
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

    The function iterates through the dataset and extracts series of output gap values based on the specified criteria.

    If during_crisis is True:
        it extracts series for each banking crisis, spanning from the year before the crisis starts (ts-1) to the year before the crisis ends (te-1)
        but stops if an exluded year occurs.
    If during_crisis is False:
        it extracts series for each recovery period, spanning from the year after the crisis ends to the year before the next crisis starts
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

    for index, row in data.iterrows():
        # Extract the serie only if the value of the value of the inflation rate is not a NaN value
        if during_crisis:
            # Extract data during a crisis
            if row['banking_crisis_only'] == 1:
                if not crisis_started:
                    crisis_started = True
                    if row['banking_crisis_only_first_year'] == 1 and index - 1 >= 0:
                        # Append the inflation rate from ts-1 to ts
                        current_serie.append(data.at[index - 1, 'output_gap'])
                        current_serie.append(row['output_gap'])
                        first_year_appended = True
                # If a crisis already begun, continue the existing serie
                else:
                    # Append only if rhe crisis continues, the first year has already been recorded, and ther is no excluded year during the crisis
                    if (row['banking_crisis_only'] == 1 and
                        first_year_appended and
                        not excluded_year_during_crisis):
                        # Continue the existing series
                        current_serie.append(row['output_gap'])
                    else:
                        excluded_year_during_crisis = True
            elif crisis_started:
                # End the series when a 0 is recorded in the banking_crisis_only column
                crisis_started = False
                # Append only if the cuurent_serie is not empty
                if len(current_serie)>0:
                    series.append(current_serie)
                current_serie = []
                first_year_appended = False
                excluded_year_during_crisis = False

        else:
            # Extract during a non-crisis period
            if row['banking_crisis_only_first_year'] == 1:
                crisis_occured = True
            elif (row['Year'] - previous_year) < 0:
                crisis_occured = False

            if row['recovery_only'] == 1:
                if crisis_occured and not excluded_year_during_recovery:
                    recovery_started = True
                    current_serie.append(row['output_gap'])
            elif row['excluded_years'] == 1  and row['banking_crisis'] != 1:
                excluded_year_during_recovery = True
            elif recovery_started:
                # End the series when a 0 is recorded in the banking_crisis column
                recovery_started = False
                series.append(current_serie)
                current_serie = []
                excluded_year_during_recovery = False
            else:
                excluded_year_during_recovery = False
        previous_year = row['Year']
    if len(current_serie)>0:
        series.append(current_serie)
    return series
