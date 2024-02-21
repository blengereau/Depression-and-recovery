import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Compute the average pattern for a given list of time series
def compute_pattern(list):
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

    return pattern


#Plot the response pattern for each length of crisis

def plot_by_crisis_length(series, crisis_duration, len_freq, string):
    for i in len_freq.Length:
        series_by_crisis_length = []
        #Appending the series for single year crisis
        for j in range (0,len(series)):
            if crisis_duration[j] == i:
                series_by_crisis_length.append(series[j])
        print(len(series_by_crisis_length))

        average_pattern = compute_pattern(series_by_crisis_length)
        # confidence_interval = 1.96 * np.std(normalize_crisis_data(series_by_crisis_length, axis=0) / np.sqrt(series_by_crisis_length.shape[0])

        if i == 1:
            years = [f"ts{k}" if k < 0
                    else f"te+{k}" if k > 0
                    else "ts = te"
                    for k in range(-1, len(average_pattern) - 1)]
        else:
            years = [f"ts{k}" if k < 0
                    else f"ts" if k == 0
                    else f"ts+{k}" if 0 < k < i
                    else "te" if k == i
                    else f"te+{k}"
                    for k in range(-1, len(average_pattern) - 1)]

        sns.lineplot(x = years, y = average_pattern, marker = 's', alpha = 0.9)
        plt.axhline(y=0, color='black', label='y=0', linestyle = 'dashed', alpha = 0.7)

        plt.plot(years[1:1+i], average_pattern[1:1+i], marker='s', color='red', label = 'Crisis period')  # Change marker color to red for example

        plt.title(f'{string} in reaction to a {i}-year crisis')
        plt.legend()

        if string == 'Inflation rate':
            plt.ylabel('Annual inflation rate')
        elif string == 'Output gap':
            plt.ylabel('Output gap')

        plt.xlabel('Time in years')
        plt.ylim(-10, 15)

        plt.show()

def plot_dynamics(crisis_series, recovery_series, string):
    #Compute the average response pattern by time elapsed with normalizing the inflation series
    pattern_during_crisis = compute_pattern(crisis_series)
    pattern_during_recovery = compute_pattern(recovery_series)

    #Compute the average response pattern by time elapsed without normalizing the inflation series
    # pattern_during_crisis = compute_pattern(crisis_data(global_data, during_crisis = True))
    # pattern_during_recovery = compute_pattern(crisis_data(global_data, during_crisis = False))

    #Plot the inflation rate during banking crsis period
    years = [f"ts{i}" if i < 0 else f"ts+{i}" if i > 0 else "ts" for i in range(-1, len(pattern_during_crisis) - 1)]
    sns.lineplot(x = years, y = pattern_during_crisis, marker = 's', label = 'During crisis')

    plt.axhline(y=0, color='orange', label='y=0', linestyle = 'dashed', alpha = 0.8)

    plt.title(f'{string} during crisis period')

    plt.xlabel('Time in years')
    plt.ylabel(string)

    plt.show()

    #Plot the inflation rate during recovery period
    years = [f"te+{i}" if i > 0 else "te" for i in range(0, len(pattern_during_recovery))]
    sns.lineplot(x = years, y = pattern_during_recovery, marker = 's', color = 'Purple', alpha = 0.9, label = 'During recovery')
    plt.axhline(y=0, color='orange', label='y=0', linestyle = 'dashed', alpha = 0.8)

    plt.title(f'{string} during recovery period')

    plt.xlabel('Time in years')
    plt.ylabel(string)
    plt.ylim(-10, 10)
    plt.xlim('te', 'te+13')
    plt.legend()

    plt.show()
