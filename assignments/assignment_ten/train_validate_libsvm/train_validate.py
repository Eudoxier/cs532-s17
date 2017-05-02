#!/usr/bin/python env
"""train_validate.py

Train a classifier and then predict values.

"""

import sys
import yaml
from pandas_ml import ConfusionMatrix
from tabulate import tabulate
from sklearn.svm import SVC
from sklearn.svm import libsvm
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
from lib.split import split, k_combinations

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

    SVC wants parrallel arrays-like objects of feature vectors
    and categories.

    """
    titles = data[0]
    word_count_vectors = data[1]
    categories = data[2]
    assert len(titles) == len(word_count_vectors) == len(categories)

    print("[*] Prepairing Classifier and Data")
    clf = SVC(kernel='rbf', probability=True)
    lable_encoder = preprocessing.LabelEncoder()
    lable_encoder.fit(list(set(categories)))

    print("[*] Normalizing Data")
    norm_data = normalize_data(data, lable_encoder)

    print("[*] Dividing Data into Training/Testing")
    training, validation = split_data(norm_data, training_percent)

    #norm_training = normalize_data(training, lable_encoder)
    #norm_validation = normalize_data(validation, lable_encoder)

    print("[*] Training...")
    training_features = training[1]
    training_classifications = training[2]
    clf.fit(training_features, training_classifications)

    print("[*] Testing...")
    validation_features = validation[1]

    print("[*] Getting Statistics")
    validation_categories = lable_encoder.inverse_transform(validation[2])

    # Standard
    predicted = clf.predict(validation_features)
    predicted_str = lable_encoder.inverse_transform(predicted)
    c_matrix = ConfusionMatrix(validation_categories, predicted_str)

    # Cross-Validation manual
    cross_results = cross_validation(norm_data, lable_encoder)

    results = zip(titles, predicted_str, categories)

    print("[*] Saving Results")
    save_results(results, "svm", c_matrix, title='SVM Training/Testing = 90/10',
                 cross_c_matrix=cross_results)


def cross_validation(data, lable_encoder):
    """Get results from cross validation.

    """
    print("[*] Getting k-fold Training/Testing split")
    training_validation = k_split(data)

    print("[*] Performing cross validation...")

    with progressbar.ProgressBar(max_value=len(training_validation)) as pbar:
        c_matrices = []
        for training, validation in training_validation:

            # Reset
            clf = SVC(kernel='rbf', probability=True)

            # Train
            training_features = training[1]
            training_classifications = training[2]
            clf.fit(training_features, training_classifications)

            # Test
            validation_features = validation[1]
            validation_categories = lable_encoder.inverse_transform(
                validation[2])

            predicted = clf.predict(validation_features)
            predicted_str = lable_encoder.inverse_transform(predicted)
            c_matrix = ConfusionMatrix(validation_categories, predicted_str)

            c_matrices.append(c_matrix)

            pbar += 1

    return c_matrices


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


def k_split(data, training_percent=0.90):
    """Split data set up k-fold by percentage.

    """
    # Get data to be sorted
    titles = data[0]
    word_count_vectors = data[1]
    categories = data[2]
    assert len(titles) == len(word_count_vectors) == len(categories)

    # Split dictionary to get titles
    with open('../truth.yml') as category_data:
        category_dict = yaml.load(category_data)
    fold_dicts  = k_combinations(category_dict)

    with progressbar.ProgressBar(max_value=len(fold_dicts)) as pbar:

        print("[*] Getting Folds")

        folds = []
        for fold_dict in fold_dicts:

            training = fold_dict['training']

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

            folds.append((training_data, validation_data))
            pbar += 1

    return folds


def save_results(results, name, c_matrix, title='title',
                 cross_c_matrix=None, cross_results=None):
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

    plot_cm(c_matrix, name)
    plot_cm(c_matrix, name, annotations=True)

    if cross_results:
        with open("tables/" + name + "_cross.rst", "w+") as out:
                out.write(rst_table)
        with open("tables/" + name + "_cross.tex", "w+") as out:
                out.write(rst_table)
        with open("stats/" + name + "_cross.txt", "w+") as out:
                out.write(rst_table)

        for result in cross_results:
            with open("tables/" + name + ".rst", "a") as out:
                out.write(rst_table)
                out.write("\n" + "=" * 72 + "\n")
            with open("tables/" + name + ".tex", "a") as out:
                out.write(tex_table)
                out.write("\n\n")

    if cross_c_matrix:

        subplot_cms(cross_c_matrix)

        with open("stats/" + name + "_cross.txt", "w+") as out:
                out.write("Each result in cross-validation\n\n" +
                          "=" * 72 + "\n\n")

        for idx, matrix in enumerate(cross_c_matrix):
            plot_cm(matrix, name + "fold" + str(idx))
            plot_cm(matrix, name + "fold" + str(idx), annotations=True)
            with open("stats/" + name + "_cross.txt", "a") as out:
                stats_dict = matrix.stats()
                cm = stats_dict['cm']
                class_ = stats_dict['class']
                out.write("{}\n\n{}".format(cm, class_))
                out.write("\n" + "=" * 72 + "\n")


def plot_cm(c_matrix, name, title='title', annotations=False):
    """Plot confusion matrix heatmap.

    """
    c_df = c_matrix.to_dataframe()
    cmap = 'viridis'

    plt.figure(figsize=(20, 20))
    plt.title(title)
    plt.rcParams["axes.labelsize"] = 15
    sns.set(font_scale=2, context='poster')
    sns.heatmap(c_df,
                annot=annotations,
                cmap=cmap,
                square=True,
                linewidths=3,
                linecolor='black')

    if annotations:
        filename = "heatmaps/" + name + "_annot" + ".png"
    else:
        filename = "heatmaps/" + name + ".png"

    plt.savefig(filename,
                format='png',
                transparent=True,
                square=True)
    plt.clf()


def subplot_cms(cms, title='title'):
    """Confusion matrix subplots.

    """

    plt.clf()

    cmap = 'viridis'
    plt.title(title)
    plt.figure(figsize=(30, 30))
    plt.rcParams["axes.labelsize"] = 20

    dfs = map(ConfusionMatrix.to_dataframe, cms)
    sns.set(context='notebook')

    y = 0
    fig, axs = plt.subplots(ncols=3, nrows=3)
    for df, idx in enumerate(dfs):
        sns.heatmap(df,
                    square=True,
                    linewidths=2,
                    linecolor='black',
                    ax=axs[idx % 3][y])
        if idx % 3 == 0:
            y += 1

    plt.savefig("heatmaps/" + "cross_validation_grid" + ".png",
                format='png',
                transparent=True,
                square=True)


if __name__ == "__main__":
    run()
