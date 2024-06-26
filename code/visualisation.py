import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def compute_pattern(list):
    '''
    Computes the average pattern and number of data points for each position in the given list of lists.

    Args:
    - lst (list): A list of lists, where each sublist represents a series of data.

    Returns:
    - np.array: An array representing the average pattern across all sublists.
    - list: A list containing the number of data points for each position in the pattern.
    '''

    nb_data_points = []
    max_length = max(len(sublist) for sublist in list)

    # Initialize an array for the average pattern
    pattern = np.zeros(max_length)

    # Iterate through each position in the pattern
    for i in range(max_length):
        # Initialize variables for the sum and length for each position
        col_sum = 0
        length = 0

        # Iterate through each sublist
        for sublist in list:
            # Check if the current sublist has a value at the current position
            if i < len(sublist):
                col_sum += sublist[i]
                length += 1

        # Calculate the mean for the current position
        mean = col_sum / length if length > 0 else 0

        # Set the mean in the average pattern array
        pattern[i] = mean
        nb_data_points.append(length)

    return pattern, nb_data_points


def plot_all_crisis_length(series, crisis_duration, frequency_table, string):
    '''
    Plots the average reaction of a list of lists to banking crises of different lengths.

    Args:
    - series (list): A list of lists, where each sublist represents a series of data.
    - crisis_duration (list): A list containing the duration of each crisis in years.
    - frequency_table (DataFrame): A DataFrame containing the frequency of each crisis duration.
    - string (str): A string indicating the variable being plotted (e.g., "Inflation rate", "Output gap").
    '''

    # Loop through each crisis duration in the frequency table
    for i in frequency_table['Length in years']:
        series_by_crisis_length = []

        #Appending the series for single year crisis
        for j in range (0,len(series)):
            if crisis_duration[j] == i:
                series_by_crisis_length.append(series[j])

        # Compute the average pattern and number of data points for the current crisis duration
        number_of_observations = len(series_by_crisis_length)
        average_pattern, number_of_data_points = compute_pattern(series_by_crisis_length)
        # confidence_interval = 1.96 * np.std(normalize_crisis_data(series_by_crisis_length, axis=0) / np.sqrt(series_by_crisis_length.shape[0])

        # Define years for x-axis labeling
        years = [f"ts{k}" if k < 0
                else f"ts" if k == 0
                else f"ts+{k}" if 0 < k < i
                else "te" if k == i
                else f"te+{k - i}"
                for k in range(-1, len(average_pattern) - 1)]

        # Plotting
        sns.set_style("whitegrid")
        sns.lineplot(x = years, y = average_pattern, marker='o', alpha=0.9, label='Average Trend')
        sns.lineplot(x = years[1:1+i], y = average_pattern[1:1+i], marker='s', color='red', label = 'Crisis period')  # Change marker color to red for example

        # Add horizontal line at y=0 and annotations for number of data points
        plt.axhline(y=0, color='black', label='y=0', linestyle = 'dashed', alpha = 0.6)
        for m in range(len(average_pattern)):
            if -10< average_pattern[m] <10:
                plt.text(m, average_pattern[m] + 0.5 , str(number_of_data_points[m]), ha='center', va='bottom')

        # Add annotations for number of observations and explanation
        plt.text(0,9,f'Number of observations : {number_of_observations}',ha='left', va='top',  style = 'italic', fontsize=10, bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 10})
        # plt.text(-0.5, -13, 'The number of points from which the average is calculated\nis indicated above each trend point.', ha='left', va='top',style = 'italic', fontsize=10, color = 'gray')

        # Set title, labels, and limits
        plt.title(f'{string} in reaction to a {i}-year banking crisis')
        plt.legend(loc='upper right')

        if string == 'Inflation rate':
            plt.ylabel('Annual inflation rate')
        elif string == 'Output gap':
            plt.ylabel('Output gap')

        plt.xlabel('Time in years')
        plt.ylim(-10, 10)

        plt.show()

def plot_by_crisis_length(series, crisis_duration, frequency_table, string, desired_length):
    '''
    Plots the average reaction of a list of lists to banking crises of a specified length.

    Args:
    - series (list): A list of lists, where each sublist represents a series of inflation rate or output gap.
    - crisis_duration (list): A list containing the duration of each crisis in years.
    - frequency_table (DataFrame): A DataFrame containing the frequency of each crisis duration.
    - string (str): A string indicating the variable being plotted (e.g., "Inflation rate", "Output gap").
    - desired_length (int): The desired length of the banking crisis to plot.
    '''

    i = desired_length #Reassign the desired_length to a variable i for convenience

    # Check if the desired length is in the frequency table
    if i in frequency_table['Length in years'].tolist():
        series_by_crisis_length = []

        #Appending the series for single year crisis
        for j in range (0,len(series)):
            if crisis_duration[j] == i:
                series_by_crisis_length.append(series[j])

        # Compute the average pattern and number of data points for the crises of desired length
        number_of_observations = len(series_by_crisis_length)
        average_pattern, number_of_data_points = compute_pattern(series_by_crisis_length)
        # confidence_interval = 1.96 * np.std(normalize_crisis_data(series_by_crisis_length, axis=0) / np.sqrt(series_by_crisis_length.shape[0])

        # Define years for x-axis labeling
        years = [f"ts{k}" if k < 0
                else f"ts" if k == 0
                else f"ts+{k}" if 0 < k < i
                else "te" if k == i
                else f"te+{k - i}"
                for k in range(-1, len(average_pattern) - 1)]

        # Plotting
        sns.set_style("whitegrid")
        sns.lineplot(x = years, y = average_pattern, marker='o', alpha=0.9, label='Average Pattern')
        sns.lineplot(x = years[1:1+i], y = average_pattern[1:1+i], marker='s', color='red', label = 'Crisis period')  # Change marker color to red for example
        plt.axhline(y=0, color='black', linestyle = 'dashed', alpha = 0.6)


        # Add annotations for number of data points
        for m in range(len(average_pattern)):
            if -10< average_pattern[m] <10:
                plt.text(m, average_pattern[m] + 0.5 , str(number_of_data_points[m]), ha='center', va='bottom')

        # Add annotations for number of observations and explanation
        plt.text(0, 9,f'Number of observations : {number_of_observations }',ha='left', va='top',  style = 'italic', fontsize=10, bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 10})
        # plt.text(-0.5, -13, 'The number of points from which the average is calculated\nis indicated above each trend point.', ha='left', va='top',style = 'italic', fontsize=10, color = 'gray')

        # Set title, labels, and limits
        plt.title(f'{string} in reaction to a {i}-year banking crisis')
        plt.legend(loc='upper right')

        if string == 'Inflation rate':
            plt.ylabel('Annual inflation rate')
        elif string == 'Output gap':
            plt.ylabel('Output gap')

        plt.xlabel('Time in years')
        plt.ylim(-10, 10)
        plt.savefig(f'../figures/inflation_to_{desired_length}_years_crisis')
        plt.show()
    else:
        print("Error: The database does not contain any examples of banking crises of the specified duration.")

def plot_dynamics(crisis_series, recovery_series, string):
    '''
    Plots the dynamics of inflation rates during crisis and recovery periods.

    Args:
    - crisis_series (list): List of lists containing inflation series during crisis periods.
    - recovery_series (list): List of lists containing inflation series during recovery periods.
    - string (str): The string indicating the type of data being plotted (Inflation rate or Output gap).

    Returns:
    None
    '''
    #Compute the average response pattern by time elapsed with normalizing the inflation series
    average_pattern_during_crisis, number_of_data_points_during_crisis  = compute_pattern(crisis_series)
    average_pattern_during_recovery, number_of_data_points_during_recovery = compute_pattern(recovery_series)

    fig, axs = plt.subplots(2, 1, figsize=(8,9), sharey = True)

    #Plot the crisis trend

    years = [f"ts{i}" if i < 0 else f"ts+{i}" if i > 0 else "ts" for i in range(-1, len(average_pattern_during_crisis) - 1)]
    sns.lineplot(ax = axs[0], x = years, y = average_pattern_during_crisis, marker = 's', label = 'Average response')
    # Add data points count to the plot
    offset = 0.1
    for m in range(len(average_pattern_during_crisis)):
        if -10< (average_pattern_during_crisis[m] + offset) <10:
            axs[0].text(m, average_pattern_during_crisis[m] + offset, str(number_of_data_points_during_crisis[m]), ha='center', va='bottom')
    # Add horizontal line at y=0
    axs[0].axhline(y=0, color='orange', label='y=0', linestyle = 'dashed', alpha = 0.8)
    # Add a box for the number of observations
    axs[0].text(0.05, 0.93,f'Number of observations : {len(crisis_series)}',ha='left', va='top',  style = 'italic', fontsize=9, bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 10}, transform=axs[0].transAxes)
    # Set plot title, labels, limits, and legend
    axs[0].legend(loc='upper right')
    axs[0].set_title(f'{string} during crisis period')
    axs[0].set_xlabel('Time in years')
    axs[0].set_ylabel(string)

    #Plot the recovery trend

    years = [f"te+{i}" if i > 0 else "te" for i in range(0, len(average_pattern_during_recovery))]
    sns.lineplot(ax=axs[1], x = years, y = average_pattern_during_recovery, marker = 's', color = 'Purple', alpha = 0.9, label = 'Average trend')
    # Add data points count to the plot
    offset = 0.3
    for m in range(0, min(14, len(average_pattern_during_recovery))):
        if -10< (average_pattern_during_recovery[m] + offset) <10:
            axs[1].text(m, average_pattern_during_recovery[m] + offset, str(number_of_data_points_during_recovery[m]), ha='center', va='bottom')
    # Add horizontal line at y=0
    axs[1].axhline(y=0, color='orange', label='y=0', linestyle = 'dashed', alpha = 0.8)
    # Add a box for the number of observations
    axs[1].text(0.05, 0.93,f'Number of observations : {len(recovery_series)}',ha='left', va='top',  style = 'italic', fontsize=9, bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 10}, transform=axs[1].transAxes)
    # Set plot title, labels, limits, and legend
    axs[1].legend(loc='upper right')
    axs[1].set_title(f'{string} during recovery period')
    axs[1].set_xlabel('Time in years')
    axs[1].set_ylabel(string)
    # axs[1].set_ylim(-6,8)

    if len(average_pattern_during_recovery) > 14:
        axs[1].set_xlim( -0.5,'te+13')

    # Separate the two subplots
    plt.subplots_adjust(hspace=0.25)
    # Add a text
    fig.text(0.12, 0, 'The number of points from which the average is calculated is diplayed above each point.', ha='left', va='bottom',style = 'italic', fontsize=10, color = 'gray')
