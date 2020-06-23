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

    Date: 6/8/2020
    Author: Haoran Fei
    Script to perform article-specific analytics, as outlined in part I of Preliminary Data
    Analysis Planning.

'''

import sys
import getopt
#import pandas as pd
import matplotlib.pyplot as plt
import engine
import os


def main(argv): 
    '''Main routine to load files, compute aggregate statistics, per-article statistics and
    sliding window analysis.'''

    article_analysis_engine = engine.Engine()
    article_analysis_engine.get_command_line_input(argv)
    article_analysis_engine.set_key("article", "title")
    article_analysis_engine.open_log_file()
    article_analysis_engine.display_aggregate_stats()
    #article_analysis_engine.iterate_per_key(article_analysis_engine.display_per_group_stats)
    #article_analysis_engine.iterate_per_key(article_analysis_engine.plot_evolution_across_time)
    article_analysis_engine.iterate_per_key(article_analysis_engine.sliding_window_analysis)

    articles_with_non_zero_scores = []
    means = dict()
    medians = dict()
    columns = article_analysis_engine.columns_to_count

    for column in columns:
        means[column] = []
        medians[column] = []

    def compute_mean_and_median_non_zero(group, group_key, index):
        # Get the edits with non-zero ores score for time-series analysis
        non_zero_articles = group.loc[group["ores_damaging"] != 0].copy()
        non_zero_count = non_zero_articles.shape[0]
        if non_zero_count != 0:
            articles_with_non_zero_scores.append(article)
            for column in columns_to_count:
                means[column].append(non_zero_articles[column].mean())
                medians[column].append(non_zero_articles[column].median())

    article_analysis_engine.iterate_per_key(compute_mean_and_median_non_zero)

    # Distribution of mean and median scores across articles
    fig, axes = plt.subplots(2, len(columns))
    fig.set_size_inches(37, 21)
    for i in range(len(columns)):
        axes[0][i].hist(means[columns[i]], bins=50)
        axes[0][i].set_title("Mean of {} across all articles".format(columns[i]))
        axes[1][i].hist(medians[columns[i]], bins=50)
        axes[1][i].set_title("Median of {} across all articles".format(columns[i]))
    plt.savefig("./graphs/aggregate/Mean_median_all_articles_all_columns_no_zero.png")
    plt.close()

    article_analysis_engine.cleanup()

if __name__ == "__main__":
    main(sys.argv[1:])