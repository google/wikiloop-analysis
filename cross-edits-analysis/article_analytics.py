'''
    Date: 6/8/2020
    Author: Haoran Fei
    Script to perform article-specific analytics, as outlined in part I of Preliminary Data
    Analysis Planning.

'''

import sys
import getopt
#import pandas as pd
import matplotlib.pyplot as plt
import loader


def main(argv): # pylint: disable=C0116

    data_file_path = ""
    range_start = 0
    range_end = 0

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
            range_start = int(value)
        else:
            range_end = int(value)

    data_loader = loader.Loader()

    if data_file_path[-5:] == ".json":
        data_loader.load_json(data_file_path, range_start, range_end)
        df = data_loader.get_data() # pylint: disable=C0103
    elif data_file_path[-4:] == ".csv":
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


    # Per-article statistics
    article_titles = df.title.unique()
    print("There are {} unique articles. The First 5 titles are: ".format(len(article_titles)))
    for i in range(min(5, len(article_titles))):
        print(article_titles[i])

    for article in article_titles:
        print("Now displaying statistics for article {}".format(article))
        edits_on_article = df.loc[df["title"] == article]
        columns_to_count = ["ores_damaging", "ores_goodfaith"]
        fig, axes = plt.subplots(1, 2)
        fig.set_size_inches(18.5, 10.5)
        i = 0
        for column in columns_to_count:
            print("The mean of {} is {}".format(column, edits_on_article[column].mean()))
            print("The median of {} is {}".format(column, edits_on_article[column].median()))
            print("The std of {} is {}".format(column, edits_on_article[column].std()))
            axes[i].hist(edits_on_article[column], bins=20)
            axes[i].set_title("Distribution of {} for article {}".format(column, article))
            i += 1
        # Path cannot contain /, but some wikipedia article names contain the "/"
        # character, which we must remove
        plt.savefig("./graphs/article/Distribution_{}.png".format(article.replace("/", "")))

if __name__ == "__main__":
    main(sys.argv[1:])
