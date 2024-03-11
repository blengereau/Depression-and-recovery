import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Compute the average pattern for a given list of time series
def compute_pattern(list):
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


#Plot the response pattern for each length of crisis

def plot_all_crisis_length(series, crisis_duration, frequency_table, string):
    for i in frequency_table.Length_of_crisis:
        series_by_crisis_length = []
        #Appending the series for single year crisis
        for j in range (0,len(series)):
            if crisis_duration[j] == i:
                series_by_crisis_length.append(series[j])

        number_of_observations = len(series_by_crisis_length)

        average_pattern, number_of_data_points = compute_pattern(series_by_crisis_length)
        # confidence_interval = 1.96 * np.std(normalize_crisis_data(series_by_crisis_length, axis=0) / np.sqrt(series_by_crisis_length.shape[0])

        # Define years for x-axis labels based on the crisis length i
        # if i == 1:
        #     years = [f"ts{k}" if k < 0
        #             else f"ts" if k == 0
        #             else "te" if k == i
        #             else f"te+{k}" if k > 0
        #             else "ts = te"
        #             for k in range(-1, len(average_pattern) - 1)]
        # else:
        years = [f"ts{k}" if k < 0
                else f"ts" if k == 0
                else f"ts+{k}" if 0 < k < i
                else "te" if k == i
                else f"te+{k - i}"
                for k in range(-1, len(average_pattern) - 1)]

        sns.set_style("whitegrid")
        sns.lineplot(x = years, y = average_pattern, marker='o', alpha=0.9, label='Average Pattern')
        sns.lineplot(x = years[1:1+i], y = average_pattern[1:1+i], marker='s', color='red', label = 'Crisis period')  # Change marker color to red for example

        plt.axhline(y=0, color='black', label='y=0', linestyle = 'dashed', alpha = 0.6)
        for m in range(len(average_pattern)):
            if -10< average_pattern[m] <10:
                plt.text(m, average_pattern[m] + 0.5 , str(number_of_data_points[m]), ha='center', va='bottom')

        plt.text(0,9,f'Number of observations : {number_of_observations}',ha='left', va='top',  style = 'italic', fontsize=10, bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 10})
        plt.text(-0.5, -13, 'The number of points from which the average is calculated \nis indicated above each trend point.', ha='left', va='top',style = 'italic', fontsize=10, color = 'gray')

        plt.title(f'{string} in reaction to a {i}-year banking crisis')
        plt.legend()

        if string == 'Inflation rate':
            plt.ylabel('Annual inflation rate')
        elif string == 'Output gap':
            plt.ylabel('Output gap')

        plt.xlabel('Time in years')
        plt.ylim(-10, 10)

        plt.show()

def plot_by_crisis_length(series, crisis_duration, frequency_table, string, desired_length):
    i = desired_length
    if i in frequency_table.Length_of_crisis.tolist():
        series_by_crisis_length = []
        #Appending the series for single year crisis
        for j in range (0,len(series)):
            if crisis_duration[j] == i:
                series_by_crisis_length.append(series[j])

        number_of_observations = len(series_by_crisis_length)

        average_pattern, number_of_data_points = compute_pattern(series_by_crisis_length)
        # confidence_interval = 1.96 * np.std(normalize_crisis_data(series_by_crisis_length, axis=0) / np.sqrt(series_by_crisis_length.shape[0])

        years = [f"ts{k}" if k < 0
                else f"ts" if k == 0
                else f"ts+{k}" if 0 < k < i
                else "te" if k == i
                else f"te+{k - i}"
                for k in range(-1, len(average_pattern) - 1)]

        sns.set_style("whitegrid")
        sns.lineplot(x = years, y = average_pattern, marker='o', alpha=0.9, label='Average Pattern')
        sns.lineplot(x = years[1:1+i], y = average_pattern[1:1+i], marker='s', color='red', label = 'Crisis period')  # Change marker color to red for example
        plt.axhline(y=0, color='black', linestyle = 'dashed', alpha = 0.6)

        for m in range(len(average_pattern)):
            if -10< average_pattern[m] <10:
                plt.text(m, average_pattern[m] + 0.5 , str(number_of_data_points[m]), ha='center', va='bottom')

        plt.text(0, 9,f'Number of observations : {number_of_observations }',ha='left', va='top',  style = 'italic', fontsize=10, bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 10})
        plt.text(-0.5, -13, 'The number of points from which the average is calculated \nis indicated above each trend point.', ha='left', va='top',style = 'italic', fontsize=10, color = 'gray')


        plt.title(f'{string} in reaction to a {i}-year banking crisis')
        plt.legend()

        if string == 'Inflation rate':
            plt.ylabel('Annual inflation rate')
        elif string == 'Output gap':
            plt.ylabel('Output gap')

        plt.xlabel('Time in years')
        plt.ylim(-10, 10)

        plt.show()
    else:
        print("Error: The database does not contain any examples of banking crises of the specified duration.")

def plot_dynamics(crisis_series, recovery_series, string):
    #Compute the average response pattern by time elapsed with normalizing the inflation series
    average_pattern_during_crisis, number_of_data_points_during_crisis  = compute_pattern(crisis_series)
    average_pattern_during_recovery, number_of_data_points_during_recovery  = compute_pattern(recovery_series)

    #Compute the average response pattern by time elapsed without normalizing the inflation series
    # pattern_during_crisis = compute_pattern(crisis_data(global_data, during_crisis = True))
    # pattern_during_recovery = compute_pattern(crisis_data(global_data, during_crisis = False))

    #Plot the inflation rate during banking crsis period
    years = [f"ts{i}" if i < 0 else f"ts+{i}" if i > 0 else "ts" for i in range(-1, len(average_pattern_during_crisis) - 1)]
    sns.lineplot(x = years, y = average_pattern_during_crisis, marker = 's', label = 'Average pattern')
    offset = 0.1
    for m in range(len(average_pattern_during_crisis)):
        if -10< (average_pattern_during_crisis[m] + offset) <10:
            plt.text(m, average_pattern_during_crisis[m] + offset, str(number_of_data_points_during_crisis[m]), ha='center', va='bottom')

    plt.axhline(y=0, color='orange', label='y=0', linestyle = 'dashed', alpha = 0.8)

    plt.title(f'{string} during crisis period')
    plt.xlabel('Time in years')
    plt.ylabel(string)
    plt.show()

    #Plot the inflation rate during recovery period
    years = [f"te+{i}" if i > 0 else "te" for i in range(0, len(average_pattern_during_recovery))]
    sns.lineplot(x = years, y = average_pattern_during_recovery, marker = 's', color = 'Purple', alpha = 0.9, label = 'Pattern during recovery')
    offset = 0.3
    for m in range(0,14):
        if -10< (average_pattern_during_recovery[m] + offset) <10:
            plt.text(m, average_pattern_during_recovery[m] + offset, str(number_of_data_points_during_recovery[m]), ha='center', va='bottom')

    plt.axhline(y=0, color='orange', label='y=0', linestyle = 'dashed', alpha = 0.8)

    plt.title(f'{string} during recovery period')

    plt.xlabel('Time in years')
    plt.ylabel(string)
    plt.ylim(-10, 10)
    plt.xlim('te', 'te+13')
    plt.legend()

    plt.show()
