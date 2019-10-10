"""
This file does some basic analysis on the hyperedges generated.
This is to compare the generated graph with the "implicit" network that we have in the database.
"""

from PostgresConnector import PostgresConnector

import numpy as np
import matplotlib.pyplot as plt

from pprint import PrettyPrinter
from collections import Counter


def reduction(result):
    """
    Prints the reduction of values.
    :param result: Contains two results.
    :return: None. Prints.
    """
    print("Reduction of values by {:.2f} %".format((1 - result[1] / result[0]) * 100))


def print_result(result):
    """
    Helper function
    :param result: Contains an array of lenghts
    :return: None. Prints only.
    """
    print("\tMean: {:.4f}".format(np.mean(result)))
    print("\tMedian: {:.4f}".format(np.median(result)))
    print("\t75-percentile: {:.4f}".format(np.percentile(result, 75)))
    print("\t99-Percentile: {:.4f}".format(np.percentile(result, 99)))
    print("\tMinimum: {}".format(np.min(result)))
    print("\tMaximum: {}".format(np.max(result)))


def get_document_table_length(prefixes, pc):
    """
    Compares the number of entries in the tables.
    :param prefixes: (list) List of prefixes for table names to compare.
    :return: None. Prints output
    """
    result = []
    for i, prefix in enumerate(prefixes):
        with pc as open_pc:
            table = prefix+"hyperedge_document"
            open_pc.cursor.execute("SELECT COUNT(*) FROM {}".format(table))
            result.append(open_pc.cursor.fetchall()[0][0])
            print("Number of documents in {}: {}".format(table, result[i]))

    if len(result) == 2:
        reduction(result)


def get_sentence_table_length(prefixes, pc):
    """
    Compares the number of entries in the tables.
    :param prefixes: (list) List of prefixes for table names to compare.
    :return: None. Prints output
    """
    result = []
    for i, prefix in enumerate(prefixes):
        with pc as open_pc:
            table = prefix+"hyperedge_sentences"
            open_pc.cursor.execute("SELECT COUNT(*) FROM {}".format(table))
            result.append(open_pc.cursor.fetchall()[0][0])
            print("Number of documents in {}: {}".format(table, result[i]))

    if len(result) == 2:
        reduction(result)


def get_hyperedge_table_length(prefixes, pc):
    """
    Compares the number of entries in the tables.
    :param prefixes: (list) List of prefixes for table names to compare.
    :return: None. Prints output
    """
    result = []
    for i, prefix in enumerate(prefixes):
        with pc as open_pc:
            table = prefix+"hyperedges"
            open_pc.cursor.execute("SELECT COUNT(*) FROM {}".format(table))
            result.append(open_pc.cursor.fetchall()[0][0])
            print("Number of hyperedge occurrences in {}: {}".format(table, result[i]))

    if len(result) == 2:
        reduction(result)


def analyze_edge_size(prefixes, pc):
    """
    Compares the number of entries per edge in the tables.
    :param prefixes: (list) List of prefixes for table names to compare.
    :return: None. Prints output
    """
    result = []
    print("Edge size analysis")
    for i, prefix in enumerate(prefixes):
        with pc as open_pc:
            table = prefix+"hyperedges"
            open_pc.cursor.execute("SELECT COUNT(*) as c FROM {} GROUP BY edge_id".format(table))

            result.append([el[0] for el in open_pc.cursor.fetchall()])

        print("Results for {}".format(table))
        print_result(result[i])


def analyze_term_frequency(prefixes, pc):
    """
    Compares the number of entries per edge in the tables.
    :param prefixes: (list) List of prefixes for table names to compare.
    :return: None. Prints output.
    """
    result = []
    print("Term frequency analysis (in edges)")
    for i, prefix in enumerate(prefixes):
        with pc as open_pc:
            table = prefix+"hyperedges"
            open_pc.cursor.execute("SELECT COUNT(*) as c FROM {} GROUP BY term_id".format(table))

            result.append([el[0] for el in open_pc.cursor.fetchall()])

        print("Results for {}".format(table))
        print_result(result[i])

def get_number_of_empty_edges(prefixes, pc):
    """
    Prints the number of empty edges.
    :param prefixes: (list) List of prefixes for table names to compare.
    :param pc: (PostgresConnector) Handle.
    :return: None. Prints output.
    """
    result = []
    print("Number of empty hyperedges:")
    for i, prefix in enumerate(prefixes):
        with pc as open_pc:
            table = prefix+"hyperedges"

            open_pc.cursor.execute("SELECT (SELECT MAX(edge_id) from {}) - "
                                   "(SELECT count(distinct edge_id) from {}) as diff".format(table, table))

            result.append(open_pc.cursor.fetchall()[0][0])
        print("Results for {}: {}".format(table, result[i]))


if __name__ == "__main__":
    prefixes = ["", "entity_"]
    pc = PostgresConnector(port=5435)
    print()
    get_document_table_length(prefixes, pc)
    print()
    get_sentence_table_length(prefixes, pc)
    print()
    get_hyperedge_table_length(prefixes, pc)
    print()
    analyze_edge_size(prefixes, pc)
    print()
    analyze_term_frequency(prefixes, pc)
    print()
    get_number_of_empty_edges(prefixes, pc)
