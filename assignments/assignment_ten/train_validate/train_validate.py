#!/usr/bin/python env
"""train_validate.py

Train a classifier and then predict values.

"""

import sys
from glob import glob
import yaml
from pandas_ml import ConfusionMatrix
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
import progressbar
import feedparser
import pci_code.docclass as docclass
import pci_code.feedfilter as feedfilter
import hy
import lib.split
import lib.utils
import lib.hyaml
import lib.sysutils
from lib.sysutils import rm
from lib.utils import confirm
from lib.split import in_half, ninety_ten

DB = 'mydb.sqlite'


def run():
    """Classify data and record the results.

    """
    import warnings
    warnings.filterwarnings("ignore")

    fisher = init()
    data = get_data()

    results_50 = half_and_half(fisher, data)
    results_90 = single_90_10(fisher, data)

    # Print some basic stats to assess the run
    print("50/50 Split: {}/{} ({}%) Correct"
          .format(results_50['correct'],
                  results_50['total'],
                  results_50['percent']))

    print("90/10 Split: {}/{} ({}%) Correct"
          .format(results_90['correct'],
                  results_90['total'],
                  results_90['percent']))


def init():
    """Nuke the database and create a new one.

    """

    rm(DB)
    fisher = docclass.fisherclassifier(docclass.getwords)
    fisher.setdb(DB)

    print("[*] Database reset")

    return fisher


def get_data():
    """Get feed data and category data then build the dictionary.

    """

    print("[*] Gathering entry and category data")

    xml_files = glob("../data/raw_xml/*.xml")
    data = {}

    # Get entry categories
    with open('../truth.yml') as category_data:
        categories = yaml.load(category_data)

    # Get entry data
    for xml in xml_files:
        print("[*] processing file {}".format(xml))
        feed_dict = feedparser.parse(xml)
        for entry in feed_dict['entries']:
            uri = entry.link
            title = entry.title
            content = entry.summary
            category = categories[title]
            data[uri] = {'title': title,
                         'content': content,
                         'category': category}

    if len(data) != 100:
        msg = "Found {}/100 entries continue anyway?".format(len(data))
        cont = confirm(msg, default='yes')
        if not cont:
            sys.exit(2)

    return data


def half_and_half(fisher, data):
    """50/50 split

    """
    training, validation = in_half(data)
    train(fisher, training)
    results = get_results(fisher, validation)
    save_results(results['data'],
                 "50_50",
                 results['c_matrix'],
                 title='Training/Testing = 50/50')

    return results


def single_90_10(fisher, data):
    """90/10 Split

    """
    training, validation = ninety_ten(data)
    train(fisher, training)
    results = get_results(fisher, validation)
    save_results(results['data'],
                 "90_10",
                 results['c_matrix'],
                 title='Training/Testing = 90/10')

    return results


def train(fisher, data):
    """Train the fisher classifier.

    """

    print("[*] Training Classifier")

    n_entries = len(data)
    with progressbar.ProgressBar(max_value=n_entries) as pbar:
        for datum in data:
            entry = data[datum]
            traning_data = entry['title'] + entry['content']
            fisher.train(traning_data, entry['category'])
            pbar += 1


def get_results(fisher, data):
    """Record the results of classification actual vs predicted.

    For each entry in the validation data, give the classifier the
    entry title and content to make a prediction, and add the
    prediction to the entry data under the key ``predicted``.

    Statistics:

        The confusion matrix is built using parallel arrays of
        actual and predicted values.

        The total number of correct predictions are tracked with
        ``correct`` but this is purely for printing some informational
        output when done running.

    Returns:

        results (dict): A dictionary holding the updated entries,
            confusion matrix, number of correct guesses, total guesses,
            and percent correct.

    """

    print("[*] Testing")

    # Data to build confusion matrix
    actual = []
    predicted = []

    correct = 0
    n_entries = len(data)
    with progressbar.ProgressBar(max_value=n_entries) as pbar:

        for datum in data:

            entry = data[datum]
            validation_data = entry['title'] + entry['content']
            category = entry['category']
            prediction = fisher.classify(validation_data, category)
            data[datum].update({"predicted": prediction})

            # Append actual and predicted to parallel lists
            # for ConfustionMatrix generation.
            actual.append(category)
            predicted.append(prediction)

            if prediction == category:
                correct += 1

            pbar += 1

    percent = (correct / len(data)) * 100
    c_matrix = ConfusionMatrix(actual, predicted)

    results = {"data": data,
               "c_matrix": c_matrix,
               "correct": correct,
               "percent": percent,
               "total": len(data)}

    return results


def save_results(data, name, c_matrix, title='title'):
    """Create a table with title and actual VS predicted

    Parameters:

        data (data): Entries with `title`, `predicted`, and `category`
            (actual) keys.

        name (str): A string for identifying the saved data by adding
            a unique identifier to the output filename.

        c_matrix (ConfusionMatrix): A instance of a pandas_ml
            ``ConfusionMatrix`` class.

    """
    results = []
    for datum in data:
        entry = data[datum]
        results += [(entry['title'], entry['predicted'], entry['category'])]

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
