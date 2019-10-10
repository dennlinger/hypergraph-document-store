"""
This file does some basic analysis on the terms generated from the documents.
Mostly, this serves the purpose of some later analysis parts in the thesis, as well as possible extensions to the
stopwords list.
"""

from TermGenerator import TermGenerator

from collections import Counter

import matplotlib.pyplot as plt
import numpy as np


def get_terms(num_distinct_documents=500,
              remove_stopwords=False,
              stopwords=[',', '.', '-', '\xa0', '“', '”', '"', '\n', '—', ':', '?', 'I', '(', ')']):
    """
    Creates TermGenerator, and parses the documents for a specific set of documents.
    :param num_distinct_documents: (int) Passed to the TermGenerator constructor, limits the size of the queries.
    :param remove_stopwords: (boolean) Whether or not stopwords should be removed.
    :param stopwords: (list of str) Contains additional stopwords that should be used. Only in conjunction with
           remove_stopwords=True
    :return: The TermGenerator object
    """
    tg = TermGenerator(num_distinct_documents=num_distinct_documents, remove_stopwords=remove_stopwords, analyze=True,
                       custom_stopwords=stopwords)
    tg.parse()

    return tg


def get_x_y_values(tg, num_words=50):
    """
    Gets a list of most frequently occurring words, with the specific number of occurrences
    :param tg: (TermGenerator) Object with the parsed sentences.
    :param num_words: (int) Number of words to be processed for the top occurring terms.
    :return: (List) List of the top N words in terms of occurrence and the respective occurrence number,
    """

    # get the most frequently occurring words
    top_occurring_words = tg.term_count.most_common(num_words)

    x = [el[0] for el in top_occurring_words]
    y = [el[1] for el in top_occurring_words]

    return x, y


def get_x_y_entities(tg, num_words=50):
    """
    Gets a list of most frequently occurring words, with the specific number of occurrences
    :param tg: (TermGenerator) Object with the parsed sentences.
    :param num_words: (int) Number of words to be processed for the top occurring terms.
    :return: (List) List of the top N words in terms of occurrence and the respective occurrence number,
    """

    # get the most frequently occurring words
    top_occurring_words = tg.entity_count.most_common(num_words)

    x = [el[0] for el in top_occurring_words]
    y = [el[1] for el in top_occurring_words]

    return x, y


def get_word_length_distribution(tg, percentile_value=95):
    """
    Returns an array of word lengths and respective occurrences, as well as display simple metrics like median.
    :param tg: (TermGenerator) Object with parsed sentences.
    :param percentile_value: (int) Percentile of the top length words
    :return: Metrics and distribution
    """

    # tricky line: Converting the mapped elments to a counter dict actually gives the length distribution right away.
    length_counter_dict = Counter(map(len, tg.term_count.elements()))

    # get them into x-y format, sorted by the key (i.e. length)
    length_sorted = sorted(length_counter_dict.items())
    x = [el[0] for el in length_sorted]
    y = [el[1] for el in length_sorted]

    # force numpy format for calculations of mean, median and percentile
    numerical_list = np.array(list(length_counter_dict.elements()))
    median = np.median(numerical_list)
    mean = np.mean(numerical_list)
    percentile = np.percentile(numerical_list, percentile_value)

    return length_counter_dict, x, y, mean, median, percentile


def get_long_words(tg, threshold=127):
    """
    Returns all words that are longer than a given threshold.
    :param tg: (TermGenerator) Object with parsed input.
    :param threshold: (int) Minimum length (in characters) of the words.
    :return: (List) All words longer than the threshold.
    """
    return [el for el in tg.terms if len(el) > threshold]


if __name__ == "__main__":
    words = 25
    thresh = 70
    top_percentile = 99
    # tg_unremoved = get_terms(remove_stopwords=False)
    # x_unremoved, y_unremoved = get_x_y_values(tg_unremoved, num_words=words)
    # a_unremoved = get_long_words(tg_unremoved, thresh)
    # print("Top words for unremoved:\n{}\n{}".format(x_unremoved, y_unremoved))
    # print("List of words longer than {} characters:\n{}\n{}".format(thresh, a_unremoved))

    tg_removed = get_terms(remove_stopwords=True)
    x_removed, y_removed = get_x_y_values(tg_removed, num_words=words)
    a_removed = get_long_words(tg_removed, thresh)

    distribution, wc_x, wc_y, mean, median, percentile = get_word_length_distribution(tg_removed, top_percentile)

    print("Word length distribution:\n{}".format(distribution))
    print("Mean length of words: {}\nMedian length of words: {}\n{}-percentile: {}".format(mean,
                                                                                           median,
                                                                                           top_percentile,
                                                                                           percentile))

    print("Top words when removed:\n{}\n{}".format(x_removed, y_removed))

    print("List of words longer than {} characters:\n{}".format(thresh, a_removed))

    fig, (ax1, ax2) = plt.subplots(1, 2)
    # plot both with/without removed words.
    ax1.bar(wc_x, wc_y)
    # for tick in ax1.get_xticklabels():
    #     tick.set_rotation(90)

    ax2.bar(x_removed, y_removed)
    for tick in ax2.get_xticklabels():
        tick.set_rotation(90)

    # store figure
    fig.savefig("./plots/top"+str(words)+"words_and_distribution.png")

    # Compute the whole distribution and plot it as a more "digestible" scatter plot with log scale maybe?
    x_all, y_all = get_x_y_values(tg_removed, num_words=2500)
    x_all_entities, y_all_entities = get_x_y_entities(tg_removed, num_words=max(2500, len(tg_removed.entity_count)))

    # TODO PLOT THE SAME BUT WITH NORMALIZED DISTRIBUTIONS!!!!

    fig2, (ax3, ax4) = plt.subplots(1,2)
    fig2.set_figwidth(15)
    ax3.plot(range(len(y_all)), y_all, label="All Terms")
    ax3.plot(range(len(y_all_entities)), y_all_entities, label="Entities")
    ax3.legend()
    ax4.plot(range(len(y_all)), y_all, label="All Terms")
    ax4.plot(range(len(y_all_entities)), y_all_entities, label="Entities")
    ax4.set_yscale("log")
    fig2.savefig("./plots/complete_word_distribution.png")
