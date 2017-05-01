#!/usr/bin/python env
"""train_validate.py

Train a classifier and then predict values.

"""

import sys
import yaml
from pandas_ml import ConfusionMatrix
from tabulate import tabulate
from sklearn.svm import SVC
from sklearn import preprocessing
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import progressbar
import feedparser
import hy
import lib.split
import lib.utils
import lib.hyaml
import lib.sysutils
from lib.utils import confirm
from lib.split import split

DB = 'mydb.sqlite'
DATA_FILE = "../data/assignment_nine_wordcount.dat"


def run():
    """Classify data and record the results.

    """
    import warnings
    warnings.filterwarnings("ignore")

    data = get_data()
    train_test(data)


def get_data():
    """Get feed data and category data then build the dictionary.

    """
    print("[*] Gathering entry and category data")

    # Get entry categories
    with open('../truth.yml') as category_data:
        category_dict = yaml.load(category_data)

    # Get vectors and titles
    with open(DATA_FILE, 'r') as data_file:
        next(data_file)
        lines = [line for line in data_file]

    titles = []
    wordcount_vectors = []
    categories = []
    for line in lines:
        tokens = line.strip().split('\t')
        title = tokens[0]
        titles.append(title)
        wordcount_vectors.append(list(map(float, tokens[1:])))
        categories.append(category_dict[title])

    entries = len(titles)
    if entries != 100:
        msg = "Found {}/100 entries continue anyway?".format(entries)
        cont = confirm(msg, default='yes')
        if not cont:
            sys.exit(2)

    return titles, wordcount_vectors, categories


def train_test(data, training_percent=0.90):
    """Split the given dataset into training and testing data then run.

    NuSVC wants parrallel arrays-like objects of feature vectors
    and categories.

    """
    titles = data[0]
    word_count_vectors = data[1]
    categories = data[2]
    assert len(titles) == len(word_count_vectors) == len(categories)

    print("[*] Prepairing Classifier and Data")
    clf = SVC(kernel='rbf')
    lable_encoder = preprocessing.LabelEncoder()
    lable_encoder.fit(list(set(categories)))

    print("[*] Dividing Data into Training/Testing")
    training, validation = split_data(data, training_percent)

    print("[*] Normalizing Data")
    norm_training = normalize_data(training, lable_encoder)
    norm_validation = normalize_data(validation, lable_encoder)

    print("[*] Training...")
    training_features = norm_training[1]
    training_classifications = norm_training[2]
    clf.fit(training_features, training_classifications)

    print("[*] Testing...")
    validation_features = norm_validation[1]

    print("[*] Getting Statistics")
    validation_categories = validation[2]
    predicted = clf.predict(validation_features)
    predicted_str = lable_encoder.inverse_transform(predicted)
    c_matrix = ConfusionMatrix(validation_categories, predicted_str)

    results = zip(titles, predicted_str, categories)

    print("[*] Saving Results")
    save_results(results, "svm", c_matrix, title='SVM Training/Testing = 90/10')


def normalize_data(data, lable_encoder):
    """Normalize the data and the categories.

    """
    titles = data[0]
    word_count_vectors = data[1]
    categories = data[2]
    assert len(titles) == len(word_count_vectors) == len(categories)

    norm_categories = lable_encoder.transform(categories)
    norm_features = preprocessing.scale(word_count_vectors)

    return titles, norm_features, norm_categories


def split_data(data, training_percent):
    """Split data set up by percentage.

    """
    # Split dictionary to get titles
    with open('../truth.yml') as category_data:
        category_dict = yaml.load(category_data)
    training, validation = split(category_dict, training=training_percent)

    # Get data to be sorted
    titles = data[0]
    word_count_vectors = data[1]
    categories = data[2]
    assert len(titles) == len(word_count_vectors) == len(categories)

    # Sort into two lists of the same form as data
    training_titles = []
    training_wcvs = []
    training_categories = []

    validation_titles = []
    validation_wcvs = []
    validation_categories = []

    training_title_keys = training.keys()
    for title, wcv, category in zip(titles, word_count_vectors, categories):
        if title in training_title_keys:
            training_titles.append(title)
            training_wcvs.append(wcv)
            training_categories.append(category)
        else:
            validation_titles.append(title)
            validation_wcvs.append(wcv)
            validation_categories.append(category)

    training_data = []
    training_data.append(training_titles)
    training_data.append(training_wcvs)
    training_data.append(training_categories)

    validation_data = []
    validation_data.append(validation_titles)
    validation_data.append(validation_wcvs)
    validation_data.append(validation_categories)

    return training_data, validation_data


def save_results(results, name, c_matrix, title='title'):
    """Create a table with title and actual VS predicted

    Parameters:

        data (data): Entries with `title`, `predicted`, and `category`
            (actual) keys.

        name (str): A string for identifying the saved data by adding
            a unique identifier to the output filename.

        c_matrix (ConfusionMatrix): A instance of a pandas_ml
            ``ConfusionMatrix`` class.

    """

    rst_table = tabulate(results, tablefmt="rst",
                         headers=["Title", "Predicted", "Actual"])

    tex_table = tabulate(results, tablefmt="latex",
                         headers=["Title", "Predicted", "Actual"])

    with open("tables/" + name + ".rst", "w+") as out:
        out.write(rst_table)
    with open("tables/" + name + ".tex", "w+") as out:
        out.write(tex_table)
    with open("stats/" + name + ".txt", "w+") as out:
        stats_dict = c_matrix.stats()
        cm = stats_dict['cm']
        class_ = stats_dict['class']
        out.write("{}\n\n{}".format(cm, class_))

    # Plot the confusion matrix
    c_df = c_matrix.to_dataframe()
    cmap = 'viridis'

    # With annotations
    plt.figure(figsize=(20, 20))
    plt.title(title)
    plt.rcParams["axes.labelsize"] = 15
    sns.set(font_scale=2, context='poster')
    sns.heatmap(c_df,
                annot=True,
                cmap=cmap,
                square=True,
                linewidths=3,
                linecolor='black')
    plt.savefig("heatmaps/" + name + "_annot" + ".png",
                format='png',
                transparent=True,
                square=True)
    plt.clf()

    # Without annotations
    plt.figure(figsize=(20, 20))
    plt.title(title)
    plt.rcParams["axes.labelsize"] = 15
    sns.set(font_scale=2, context='poster')
    sns.heatmap(c_df,
                cmap=cmap,
                square=True,
                linewidths=3,
                linecolor='black')
    plt.savefig("heatmaps/" + name + ".png",
                format='png',
                transparent=True,
                square=True)
    plt.clf()


if __name__ == "__main__":
    run()
