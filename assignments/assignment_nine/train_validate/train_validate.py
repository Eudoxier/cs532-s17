#!/usr/bin/python env
"""train_validate.py

Train a classifier and then predict values.

"""

import sys
from glob import glob
import yaml
from tabulate import tabulate
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
    fisher = init()
    data = get_data()

    percent_50, correct_50, total_50 = half_and_half(fisher, data)
    percent_90, correct_90, total_90 = single_90_10(fisher, data)

    print("50/50 Split: {}/{} ({}%) Correct"
          .format(correct_50, total_50, percent_50))
    print("90/10 Split: {}/{} ({}%) Correct"
          .format(correct_90, total_90, percent_90))


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
    results, correct, percent= get_results(fisher, validation)
    save_results(results, "50_50")
    return (percent, correct, len(validation))


def single_90_10(fisher, data):
    """90/10 Split

    """
    training, validation = ninety_ten(data)
    train(fisher, training)
    results, correct, percent = get_results(fisher, validation)
    save_results(results, "90_10")
    return (percent, correct, len(validation))


def train(fisher, data):
    """Train the fisher classifier.

    """
    for datum in data:
        entry = data[datum]
        traning_data = entry['title'] + entry['content']
        fisher.train(traning_data, entry['category'])


def get_results(fisher, data):
    """Record the results of classification actual vs predicted.

    """
    correct = 0
    for datum in data:

        entry = data[datum]
        actual = entry['category']
        validation_data = entry['title'] + entry['content']
        prediction = fisher.classify(validation_data, actual)
        print("\n\n[*] Predicted: {}\t\tActual: {}\n\n".format(prediction, actual))

        data[datum].update({"predicted": prediction})

        if prediction == entry['category']:
            correct += 1

    percent = (correct / len(data)) * 100

    return (data, correct, percent)


def save_results(data, name):
    """Create a table with title and actual VS predicted

    """

    results = []
    for datum in data:
        entry = data[datum]
        results += [(entry['title'], entry['predicted'], entry['category'])]

    rst_table = tabulate(results, tablefmt="rst",
                         headers=["Title", "Predicted", "Actual"])

    tex_table = tabulate(results, tablefmt="latex",
                         headers=["Title", "Predicted", "Actual"])

    overwrite = confirm("Overwrite tables?")
    if overwrite:
        with open("tables/" + name + ".rst", "w+") as out:
            out.write(rst_table)
        with open("tables/" + name + ".tex", "w+") as out:
            out.write(tex_table)

    print(rst_table)


if __name__ == "__main__":
    run()
