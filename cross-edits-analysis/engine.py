'''
    Copyright 2020 Google LLC

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Date: 6/19/2020
    Author: Haoran Fei
    Providing helpful utilities to assist analysis of Wikipedia edit data.

'''

import sys
import getopt
#import pandas as pd
import matplotlib.pyplot as plt
import loader
import os

class Engine:
    '''
        Analysis Engine Class. Provides Utilities such as command-line parsing, grouping
        and graphing. 
        Instance Variables:
            df: the combined dataframe supplied by the data loader class. 
            range_start: the starting index of the input files.
            range_end: the ending index of the input files. Notice that we use Pythonic
                       indexing: start is inclusive while end is exclusive.
            columns_to_count: columns that are used for analytics.
            key: the key to group the dataset by
            key_column_name: name of the key column in string.
            group_count: number of groups
            anomaly_threshold: percentage threshold for anomaly. Used for sliding window analysis.
            window_log_file: log file for anomaly incidents identified. 
        Public Methods:
            get_command_line_input: provides a standardized command-line prompt for user.
            open_log_file: opens the required log file.
            display_aggregate_stats: shows the aggregate statistics of the dataset on command line.
            set_key: set the group-by key of the analysis Engine.
            fill_in_missing_key: automatically replaces empty keys.
            iterate_per_key: core method for analysis. Iterates any number of tasks across all 
                             groups. Each task must be a method that takes in 3 arguments: 
                             the group, the group-id and the group index (in all groups).
            display_per_group_stats: a built-in task that prints each group's stats on console.
            plot_evolution_over_time: a built-in task that plots the evolution of both scores
                                      against timestamp.
            sliding_window_analysis: a built-in task to perform sliding window analysis on a group.
                                     For detailed explanation as well as formula, see README.
            cleanup: performs cleanup upon exiting.
    '''

    def __init__(self):
        self.df = None
        self.range_start = 0
        self.range_end = 1
        # Columns to consider for analysis. Subject to change. 
        self.columns_to_count = ["ores_damaging", "ores_goodfaith"]
        self.key = ""
        self.key_column_name = ""
        self.group_count = 0
        self.anomaly_threshold = 50 # >50% difference during window period is flagged as anomaly
        self.window_log_file = ""

    def get_command_line_input(self, argv):
        '''Parse the command line input that specifies data file paths.'''
        data_file_path = ""

        try:
            opts, _ = getopt.getopt(argv, "", ["path=", "start=", "stop="])
        except getopt.GetoptError:
            print("article_analytics.py --path <pattern_of_path_to_data_files> --start \
                <start_of_file_index_range> --end <end_of_file_index_range>")
            sys.exit(2)

        for option, value in opts:
            if option == "--path":
                data_file_path = value
            elif option == "--start":
                self.range_start = int(value)
            else:
                self.range_end = int(value)

        data_loader = loader.Loader()
        _, file_extension = os.path.splitext(data_file_path)

        if file_extension == ".json":
            data_loader.load_json(data_file_path, self.range_start, self.range_end)
            self.df = data_loader.get_data() 
        elif file_extension == ".csv":
            data_loader.load_csv(data_file_path, self.range_start, self.range_end)
            self.df = data_loader.get_data() 
        else:
            print("Unrecognizable data file format. Data file must be in .csv or .json format!")
            sys.exit()

    def open_log_file(self):
        '''Open(and if not present, create) an anomaly log file'''
        self.window_log_file = open("./log/{}/sliding_window_anomaly_{}_start_{}_end_{}.txt".\
                       format(self.key, self.anomaly_threshold, self.range_start, self.range_end), "w+") 

    def display_aggregate_stats(self):
        '''Show aggregate statistics of the dataset. Metrics include mean, median 
        and standard deviation.'''
        print("Now displaying aggregate statistics from {} to {}".format(self.range_start, self.range_end))
        fig, axes = plt.subplots(1, 2)
        fig.set_size_inches(18.5, 10.5)
        i = 0
        for column in self.columns_to_count:
            print("The mean of {} is {:.2f}".format(column, self.df[column].mean()))
            print("The median of {} is {:.2f}".format(column, self.df[column].median()))
            print("The std of {} is {:.2f}".format(column, self.df[column].std()))
            zero_count = self.df[self.df[column] == 0].shape[0]
            row_count = self.df.shape[0]
            print("The count of zeros of {} is {}".format(column, zero_count))
            print("The percentage of zeros of {} is {:.2f}%".format(column, zero_count / row_count))
            axes[i].hist(self.df[column], bins=20)
            axes[i].set_title("Distribution of {}".format(column))
            i += 1

        plt.savefig("./graphs/aggregate/Distribution_Agg.png")

    def set_key(self, key_string, key_column_name):
        '''Specify the key to split the dataset on. Only handles single key.'''
        self.key = key_string
        self.key_column_name = key_column_name

    def fill_in_missing_key(self):
        '''For some key columns, there exists empty values. We must replace
        them with values from other columns.'''
        if self.key == "author":
            self.df.author[self.df.author == ""] = self.df.ip 

    def iterate_per_key(self, *argv):
        '''Perform required operation on each group, grouped by key column.
           The operation must be a instance method of the Engine class.'''
        self.group_count = len(self.df[self.key_column_name].unique())
        index = 0
        for group in self.df[self.key_column_name].unique():
            for operation in argv:
                operation(self.df.loc[self.df[self.key_column_name] == group], group, index)
            index += 1

    def display_per_group_stats(self, group, group_key, index):
        '''Displays statistics of each group. Metrics include mean, median
           and standard deviation.'''
        fig, axes = plt.subplots(1, 2)
        fig.set_size_inches(18.5, 10.5)
        i = 0

        for column in self.columns_to_count:
            print("Now displaying statistics for {} {}".format(self.key, group_key))
            print("The mean of {} is {:.2f}".format(column, group[column].mean()))
            print("The median of {} is {:.2f}".format(column, group[column].median()))
            print("The std of {} is {:.2f}".format(column, group[column].std()))
            axes[i].hist(group[column], bins=20)
            axes[i].set_title("Distribution of {} for {} {}".format(column, self.key, group_key))
            i += 1
        # Path cannot contain /, but some wikipedia article names contain the "/"
        # character, which we must remove
        plt.savefig("./graphs/{}/Distribution_{}.png".format(self.key, group_key.replace("/", "")))
        plt.close()

    def plot_evolution_across_time(self, group, group_key, index):
        '''Plots the change of ores scores of a given group through time.'''
        non_zero_articles = group.loc[group["ores_damaging"] != 0].copy()
        non_zero_count = non_zero_articles.shape[0]
        non_zero_articles.sort_values(by="timestamp", ascending=True, inplace=True)
        if non_zero_count <= 1:
            return

        fig, axes = plt.subplots(1, 2)
        fig.set_size_inches(18.5, 10.5)
        i = 0
        for column in self.columns_to_count:
            axes[i].plot(non_zero_articles["timestamp"], non_zero_articles[column])
            axes[i].set_title("Change of {} for article {}".format(column, group_key))
            i += 1
        plt.savefig("./graphs/{}/Evolution_{}.png".format(self.key, group_key.replace("/", "")))
        plt.close()

    def sliding_window_analysis(self, group, group_key, index):
        '''Detect anomalies using sliding window analysis. Anomalies are
        defined to be values that deviate significantly from a period's average'''

        # Get the edits with non-zero ores score for time-series analysis
        non_zero_articles = group.loc[group["ores_damaging"] != 0].copy()
        non_zero_count = non_zero_articles.shape[0]
        # If multiplier is -1, then a higher value indicates an edit is "good" (less likely
        # to be vandalism). If multiplier is 1, then a higher value indicates an edit
        # is "bad" (more likely to be vandalism).
        # This is because for columns where higher value is "good", we only watch for
        # abnormally low values (we care less about the abnormally high values), 
        # and for columns where higher value is "bad", we only watch for the 
        # abnormally high values. 
        column_diff_multiplier = {"ores_damaging": 1, "ores_goodfaith": -1}

        # Constants for sliding window analysis
        window_size = 10
        if non_zero_count <= 1:
            return
        if non_zero_count < 10:
            window_size = 1
        non_zero_articles.sort_values(by="timestamp", ascending=True, inplace=True)

        # Sliding window analysis to identify periods of extreme values
        window_index = 0
        baselines_mean = dict()
        baselines_median = dict()
        for column in self.columns_to_count:
            baselines_mean[column] = non_zero_articles[column].mean()
            baselines_median[column] = non_zero_articles[column].median()

        while window_index + window_size <= non_zero_count: 
            window_frame = non_zero_articles[window_index: window_index + window_size]
            starting_time = non_zero_articles.iloc[window_index]["timestamp"]
            ending_time = non_zero_articles.iloc[window_index + window_size - 1]["timestamp"]
            for column in self.columns_to_count:
                mean_diff = column_diff_multiplier[column] * \
                            (window_frame[column].mean() - baselines_mean[column])
                median_diff = column_diff_multiplier[column] * \
                              (window_frame[column].median() - baselines_median[column])
                mean_diff_percent = mean_diff / baselines_mean[column] * 100.0
                median_diff_percent = median_diff / baselines_median[column] * 100.0
                if mean_diff_percent > self.anomaly_threshold:
                    self.window_log_file.write(("Anomaly of mean of {} detected for {} during " 
                        "period from {} to {}, with a {:.2f} percent difference "
                        "from baseline.\n").format(\
                        column, group_key, starting_time, ending_time, mean_diff_percent))
                if median_diff_percent > self.anomaly_threshold:
                    self.window_log_file.write(("Anomaly of median of {} detected for {} "
                        "during period from {} to {}, with a {:.2f} percent difference "
                        "from baseline.\n").format(\
                        column, group_key, starting_time, ending_time, median_diff_percent))

            window_index = window_index + 1

    def cleanup(self):
        '''Perform necessary cleanup work, like closing files.'''
        self.window_log_file.close()








