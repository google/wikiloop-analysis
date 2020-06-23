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

    Date: 6/11/2020
    Author: Haoran Fei
    Script to perform author-specific analytics, as outlined in part II of Preliminary Data
    Analysis Planning.

'''

import sys
import getopt
#import pandas as pd
import matplotlib.pyplot as plt
import loader


def main(argv): 
    '''Main routine to load files, compute aggregate statistics, per-author statistics and
    sliding window analysis.'''

    data_file_path = ""
    range_start = 0
    range_end = 0

    try:
        opts, _ = getopt.getopt(argv, "", ["path=", "start=", "stop="])
    except getopt.GetoptError:
        print("author_analytics.py --path <pattern_of_path_to_data_files> --start \
            <start_of_file_index_range> --end <end_of_file_index_range>")
        sys.exit(2)

    for option, value in opts:
        if option == "--path":
            data_file_path = value
        elif option == "--start":
            range_start = int(value)
        else:
            range_end = int(value)

    data_loader = loader.Loader()
    _, file_extension = os.path.splitext(data_file_path)

    if file_extension == ".json":
        data_loader.load_json(data_file_path, range_start, range_end)
        df = data_loader.get_data() # pylint: disable=C0103
    elif file_extension == ".csv":
        data_loader.load_csv(data_file_path, range_start, range_end)
        df = data_loader.get_data() # pylint: disable=C0103
    else:
        print("Unrecognizable data file format. Data file must be in .csv or .json format!")
        sys.exit()

    # Aggregate statistics
    print("Now displaying aggregate statistics from {} to {}".format(range_start, range_end))
    columns_to_count = ["ores_damaging", "ores_goodfaith"]
    fig, axes = plt.subplots(1, 2)
    fig.set_size_inches(18.5, 10.5)
    i = 0
    for column in columns_to_count:
        print("The mean of {} is {}".format(column, df[column].mean()))
        print("The median of {} is {}".format(column, df[column].median()))
        print("The std of {} is {}".format(column, df[column].std()))
        zero_count = df[df[column] == 0].shape[0]
        row_count = df.shape[0]
        print("The count of zeros of {} is {}".format(column, zero_count))
        print("The percentage of zeros of {} is {}%".format(column, zero_count / row_count))
        axes[i].hist(df[column], bins=20)
        axes[i].set_title("Distribution of {}".format(column))
        i += 1

    plt.savefig("./graphs/aggregate/Distribution_Agg.png")

    # Per-author statistics
    authors = df.author.unique()
    print("There are {} unique authors. The First 5 titles are: ".format(len(authors)))
    for i in range(min(5, len(authors))):
        print(authors[i])

    for author in authors:
        print("Now displaying statistics for author {}".format(author))
        edits_by_author = df.loc[df["author"] == author]
        columns_to_count = ["ores_damaging", "ores_goodfaith"]
        fig, axes = plt.subplots(1, 2)
        fig.set_size_inches(18.5, 10.5)
        i = 0
        for column in columns_to_count:
            print("The mean of {} is {}".format(column, edits_by_author[column].mean()))
            print("The median of {} is {}".format(column, edits_by_author[column].median()))
            print("The std of {} is {}".format(column, edits_by_author[column].std()))
            axes[i].hist(edits_by_author[column], bins=20)
            axes[i].set_title("Distribution of {} for author {}".format(column, author))
            i += 1
        # Path cannot contain /, but some wikipedia author names may contain the "/"
        # character, which we must remove
        plt.savefig("./graphs/author/Distribution_{}.png".format(author.replace("/", "")))

if __name__ == "__main__":
    main(sys.argv[1:])
