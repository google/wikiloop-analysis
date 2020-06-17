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
        print("The mean of {} is {:.2f}".format(column, df[column].mean()))
        print("The median of {} is {:.2f}".format(column, df[column].median()))
        print("The std of {} is {:.2f}".format(column, df[column].std()))
        zero_count = df[df[column] == 0].shape[0]
        row_count = df.shape[0]
        print("The count of zeros of {} is {}".format(column, zero_count))
        print("The percentage of zeros of {} is {:.2f}%".format(column, zero_count / row_count))
        axes[i].hist(df[column], bins=20)
        axes[i].set_title("Distribution of {}".format(column))
        i += 1

    plt.savefig("./graphs/aggregate/Distribution_Agg.png")


    # Per-article statistics
    article_titles = df.title.unique()
    print("There are {} unique articles. The First 5 titles are: ".format(len(article_titles)))
    for i in range(min(5, len(article_titles))):
        print(article_titles[i])

    columns_to_count = ["ores_damaging", "ores_goodfaith"]
    # If multiplier is -1, then a higher value indicates an edit is "good" (less likely
    # to be vandalism). If multiplier is 1, then a higher value indicates an edit
    # is "bad" (more likely to be vandalism).
    # This is because for columns where higher value is "good", we only watch for
    # abnormally low values (we care less about the abnormally high values), 
    # and for columns where higher value is "bad", we only watch for the 
    # abnormally high values. 
    column_diff_multiplier = {"ores_damaging": 1, "ores_goodfaith": -1}

    articles_with_non_zero_scores = []
    means = dict()
    medians = dict()
    anomaly_threshold = 50 # >50% difference during window period is flagged as anomaly event
    window_log_file = open("./log/article/sliding_window_anomaly_{}_start_{}_end_{}.txt". \
        format(anomaly_threshold, range_start, range_end), "w")

    for column in columns_to_count:
        means[column] = []
        medians[column] = []

    article_index = 0
    for article in article_titles:
        if article_index % 50 == 0:
            print("Now at article {}, index {}".format(article, article_index))
        article_index += 1

        edits_on_article = df.loc[df["title"] == article]
        fig, axes = plt.subplots(1, 2)
        fig.set_size_inches(18.5, 10.5)
        i = 0

        for column in columns_to_count:
            #print("The mean of {} is {:.2f}".format(column, edits_on_article[column].mean()))
            #print("The median of {} is {:.2f}".format(column, edits_on_article[column].median()))
            #print("The std of {} is {:.2f}".format(column, edits_on_article[column].std()))
            axes[i].hist(edits_on_article[column], bins=20)
            axes[i].set_title("Distribution of {} for article {}".format(column, article))
            i += 1
        # Path cannot contain /, but some wikipedia article names contain the "/"
        # character, which we must remove
        plt.savefig("./graphs/article/Distribution_{}.png".format(article.replace("/", "")))
        plt.close()

        # Get the edits with non-zero ores score for time-series analysis
        non_zero_articles = edits_on_article.loc[edits_on_article["ores_damaging"] != 0].copy()
        non_zero_count = non_zero_articles.shape[0]
        if non_zero_count != 0:
            articles_with_non_zero_scores.append(article)
            for column in columns_to_count:
                means[column].append(non_zero_articles[column].mean())
                medians[column].append(non_zero_articles[column].median())

        # Constants for sliding window analysis
        window_size = 10
        if non_zero_count <= 1:
            continue
        else:
            if non_zero_count < 10:
                window_size = 1
            non_zero_articles.sort_values(by="timestamp", ascending=True, inplace=True)
            fig, axes = plt.subplots(1, 2)
            fig.set_size_inches(18.5, 10.5)
            i = 0
            for column in columns_to_count:
                axes[i].plot(non_zero_articles["timestamp"], non_zero_articles[column])
                axes[i].set_title("Change of {} for article {}".format(column, article))
                i += 1
            plt.savefig("./graphs/article/Evolution_{}.png".format(article.replace("/", "")))
            plt.close()

            # Sliding window analysis to identify periods of extreme values
            window_index = 0
            baselines_mean = dict()
            baselines_median = dict()
            for column in columns_to_count:
                baselines_mean[column] = non_zero_articles[column].mean()
                baselines_median[column] = non_zero_articles[column].median()

            while window_index + window_size <= non_zero_count: 
                window_frame = non_zero_articles[window_index: window_index + window_size]
                starting_time = non_zero_articles.iloc[window_index]["timestamp"]
                ending_time = non_zero_articles.iloc[window_index + window_size - 1]["timestamp"]
                for column in columns_to_count:
                    mean_diff = column_diff_multiplier[column] * \
                                (window_frame[column].mean() - baselines_mean[column])
                    median_diff = column_diff_multiplier[column] * \
                                  (window_frame[column].median() - baselines_median[column])
                    mean_diff_percent = mean_diff / baselines_mean[column] * 100.0
                    median_diff_percent = median_diff / baselines_median[column] * 100.0
                    if mean_diff_percent > anomaly_threshold:
                        window_log_file.write(("Anomaly of mean of {} detected for {} during " 
                            "period from {} to {}, with a {:.2f} percent difference "
                            "from baseline.\n").format(\
                            column, article, starting_time, ending_time, mean_diff_percent))
                    if median_diff_percent > anomaly_threshold:
                        window_log_file.write(("Anomaly of median of {} detected for {} "
                            "during period from {} to {}, with a {:.2f} percent difference "
                            "from baseline.\n").format(\
                            column, article, starting_time, ending_time, median_diff_percent))

                window_index = window_index + 1

    # Distribution of mean and median scores across articles
    fig, axes = plt.subplots(2, len(columns_to_count))
    fig.set_size_inches(37, 21)
    for i in range(len(columns_to_count)):
        axes[0][i].hist(means[columns_to_count[i]], bins=50)
        axes[0][i].set_title("Mean of {} across all articles".format(columns_to_count[i]))
        axes[1][i].hist(medians[columns_to_count[i]], bins=50)
        axes[1][i].set_title("Median of {} across all articles".format(columns_to_count[i]))
    plt.savefig("./graphs/aggregate/Mean_median_all_articles_all_columns_no_zero.png")
    plt.close()

    window_log_file.close()


if __name__ == "__main__":
    main(sys.argv[1:])
